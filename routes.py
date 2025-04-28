import os
import json
import pytz
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, session, send_file, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from pdf_generator import convert_html_to_pdf, get_current_ist_time, format_ist_time
from models import User, FileUpload, Report, ChatSession, ChatMessage
from forms import RegistrationForm, LoginForm, UploadFileForm, ChatForm
from file_processor import process_uploaded_file
from ai_processor import (
    generate_balance_sheet,
    generate_income_statement,
    generate_cash_flow,
    generate_analysis,
    process_chat_query,
    explain_ai_decision
)


def register_routes(app):
    
    @app.route('/')
    def landing():
        return render_template('landing.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Login unsuccessful. Please check email and password.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('landing'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        files = FileUpload.query.filter_by(user_id=current_user.id).order_by(FileUpload.upload_date.desc()).all()
        reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.generated_date.desc()).all()
        
        return render_template('dashboard.html', files=files, reports=reports)
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            filename = secure_filename(file.filename)
            
            # Get file extension
            file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
            
            # Save file temporarily
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)
            
            # Create file upload record
            file_upload = FileUpload(
                filename=filename,
                file_type=file_ext,
                user_id=current_user.id
            )
            db.session.add(file_upload)
            db.session.commit()
            
            # Process the file
            try:
                data = process_uploaded_file(temp_path, file_ext)
                
                # Mark file as processed
                file_upload.processed = True
                db.session.commit()
                
                # Store data in session for report generation
                session['file_data'] = data
                session['file_id'] = file_upload.id
                
                flash('File uploaded and processed successfully!', 'success')
                return redirect(url_for('report_options'))
            
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'danger')
                db.session.delete(file_upload)
                db.session.commit()
            
            finally:
                # Clean up temporary file
                os.remove(temp_path)
        
        return render_template('upload.html', form=form)
    
    @app.route('/report-options')
    @login_required
    def report_options():
        if 'file_data' not in session or 'file_id' not in session:
            flash('No data available. Please upload a file first.', 'warning')
            return redirect(url_for('upload'))
        
        file_id = session['file_id']
        file = FileUpload.query.get_or_404(file_id)
        
        return render_template('report.html', file=file)
    
    @app.route('/generate-report/<report_type>')
    @login_required
    def generate_report(report_type):
        import logging
        logger = logging.getLogger('fintelligence')
        
        if 'file_data' not in session or 'file_id' not in session:
            flash('No data available. Please upload a file first.', 'warning')
            return redirect(url_for('upload'))
        
        file_data = session['file_data']
        file_id = session['file_id']
        
        logger.debug(f"Generating {report_type} report for file ID: {file_id}")
        
        try:
            # Log data before processing
            logger.debug(f"File data format: {file_data.get('format', 'unknown')}")
            logger.debug(f"File data columns: {file_data.get('columns', [])}")
            
            if report_type == 'balance_sheet':
                report_data = generate_balance_sheet(file_data)
                template = 'balance_sheet.html'
            elif report_type == 'income_statement':
                report_data = generate_income_statement(file_data)
                template = 'income_statement.html'
            elif report_type == 'cash_flow':
                report_data = generate_cash_flow(file_data)
                template = 'cash_flow.html'
            elif report_type == 'analysis':
                report_data = generate_analysis(file_data)
                template = 'fallback_financial_analysis.html'
            else:
                flash('Invalid report type.', 'danger')
                return redirect(url_for('report_options'))
            
            # Save report to database
            report = Report(
                report_type=report_type,
                data=json.dumps(report_data),
                user_id=current_user.id,
                file_id=file_id
            )
            db.session.add(report)
            db.session.commit()
            
            # Add IST datetime for all templates
            return render_template(template, report=report, data=report_data, ist_datetime=format_ist_time())
        
        except Exception as e:
            import traceback
            logger.error(f"Error generating report: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f'Error generating report: {str(e)}', 'danger')
            return redirect(url_for('report_options'))
    
    @app.route('/report/<int:report_id>')
    @login_required
    def view_report(report_id):
        report = Report.query.get_or_404(report_id)
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to view this report.', 'danger')
            return redirect(url_for('dashboard'))
        
        report_data = json.loads(report.data)
        
        if report.report_type == 'balance_sheet':
            template = 'balance_sheet.html'
        elif report.report_type == 'income_statement':
            template = 'income_statement.html'
        elif report.report_type == 'cash_flow':
            template = 'cash_flow.html'
        elif report.report_type == 'analysis':
            template = 'fallback_financial_analysis.html'
            # Add IST datetime for template
            return render_template(template, report=report, data=report_data, ist_datetime=format_ist_time())
        else:
            flash('Invalid report type.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Add IST datetime for all templates
        return render_template(template, report=report, data=report_data, ist_datetime=format_ist_time())
    
    @app.route('/download-report/<int:report_id>')
    @login_required
    def download_report(report_id):
        """Redirect to the PDF download route."""
        return redirect(url_for('download_report_pdf', report_id=report_id))
    
    @app.route('/chatbot', methods=['GET', 'POST'])
    @login_required
    def chatbot():
        form = ChatForm()
        
        # Get or create a chat session
        session_id = request.args.get('session_id')
        chat_session = None
        
        if session_id:
            chat_session = ChatSession.query.get(session_id)
            if chat_session and chat_session.user_id != current_user.id:
                chat_session = None
        
        if not chat_session:
            chat_session = ChatSession(user_id=current_user.id)
            db.session.add(chat_session)
            db.session.commit()
        
        messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
        
        if form.validate_on_submit():
            user_message = form.message.data
            
            # Save user message
            user_chat = ChatMessage(
                session_id=chat_session.id,
                is_user=True,
                message=user_message
            )
            db.session.add(user_chat)
            
            # Process with AI and get response
            user_files = FileUpload.query.filter_by(user_id=current_user.id, processed=True).all()
            file_data = []
            
            for file in user_files:
                reports = Report.query.filter_by(file_id=file.id).all()
                if reports:
                    for report in reports:
                        file_data.append({
                            'filename': file.filename,
                            'report_type': report.report_type,
                            'data': json.loads(report.data)
                        })
            
            ai_response = process_chat_query(user_message, file_data)
            
            # Save AI response
            ai_chat = ChatMessage(
                session_id=chat_session.id,
                is_user=False,
                message=ai_response
            )
            db.session.add(ai_chat)
            db.session.commit()
            
            # Refresh messages
            messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
            form.message.data = ''
        
        return render_template('chatbot.html', form=form, chat_session=chat_session, messages=messages)
    
    @app.route('/explain/<int:report_id>')
    @login_required
    def explainability(report_id):
        report = Report.query.get_or_404(report_id)
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to view this explanation.', 'danger')
            return redirect(url_for('dashboard'))
        
        report_data = json.loads(report.data)
        explanation = explain_ai_decision(report.report_type, report_data)
        
        return render_template('explainability.html', report=report, explanation=explanation)
        
    @app.route('/demo-analysis')
    @login_required
    def demo_analysis():
        """Show a demo financial analysis with static charts."""
        return render_template('demo_analysis.html')
        
    @app.route('/download-report-pdf/<int:report_id>')
    @login_required
    def download_report_pdf(report_id):
        """Download a report as PDF instead of JSON."""
        report = Report.query.get_or_404(report_id)
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to download this report.', 'danger')
            return redirect(url_for('dashboard'))
        
        report_data = json.loads(report.data)
        
        # Get file information
        file_upload = FileUpload.query.get(report.file_id)
        
        # Get current time in IST
        ist_datetime = format_ist_time()
        
        # Select appropriate PDF template based on report type
        if report.report_type == 'balance_sheet':
            template = 'balance_sheet_pdf.html'
        elif report.report_type == 'income_statement':
            template = 'income_statement_pdf.html'
        elif report.report_type == 'cash_flow':
            template = 'cash_flow_pdf.html'
        elif report.report_type == 'analysis':
            template = 'pdf_template.html'
        else:
            flash('Invalid report type for PDF generation.', 'danger')
            return redirect(url_for('view_report', report_id=report.id))
        
        # Render HTML content with the report data
        html_content = render_template(
            template,
            report=report,
            data=report_data,
            ist_datetime=ist_datetime
        )
        
        # Convert HTML to PDF
        pdf_file = convert_html_to_pdf(html_content)
        
        if not pdf_file:
            flash('Error generating PDF.', 'danger')
            return redirect(url_for('view_report', report_id=report.id))
        
        # Generate filename based on report type and date
        date_str = get_current_ist_time().strftime('%Y%m%d')
        filename = f"{report.report_type}_{date_str}.pdf"
        
        # Return PDF file
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
