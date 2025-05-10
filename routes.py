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
            
            # Check if report already exists
            existing_report = Report.query.filter_by(
                file_id=file_id,
                report_type=report_type,
                user_id=current_user.id
            ).first()
            
            # If report exists, load it
            if existing_report:
                try:
                    report_data = json.loads(existing_report.data)
                    # Ensure it's a dictionary to prevent template errors
                    if not isinstance(report_data, dict):
                        report_data = {}
                except Exception as e:
                    logger.error(f"JSON decode error for existing report: {str(e)}")
                    # Provide empty dict if there's a JSON parsing error
                    report_data = {}
                    
                if report_type == 'balance_sheet':
                    template = 'balance_sheet.html'
                elif report_type == 'income_statement':
                    template = 'income_statement.html'
                elif report_type == 'cash_flow':
                    template = 'cash_flow.html'
                elif report_type == 'analysis':
                    template = 'financial_analysis.html'
                else:
                    flash('Invalid report type.', 'danger')
                    return redirect(url_for('report_options'))
                
                return render_template(template, report=existing_report, data=report_data, ist_datetime=format_ist_time())
            
            # Generate new report
            try:
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
                    template = 'financial_analysis.html'
                else:
                    flash('Invalid report type.', 'danger')
                    return redirect(url_for('report_options'))
                
                # Ensure report_data is a dictionary to prevent template errors
                if not isinstance(report_data, dict):
                    report_data = {}
                    
                # Add required fields if missing - similar to view_report
                if report_type == 'cash_flow':
                    # Add metrics field if missing
                    if 'metrics' not in report_data:
                        report_data['metrics'] = {}
                    # Add cash_flow_statement field if missing
                    if 'cash_flow_statement' not in report_data:
                        report_data['cash_flow_statement'] = {}
                    # Add insights and recommendations if missing
                    if 'insights' not in report_data:
                        report_data['insights'] = ["Analysis of cash flow patterns is pending."]
                    if 'recommendations' not in report_data:
                        report_data['recommendations'] = ["Review your cash flow statement for further insights."]
                        
                elif report_type == 'balance_sheet':
                    # Add balance_sheet field if missing
                    if 'balance_sheet' not in report_data:
                        report_data['balance_sheet'] = {}
                    # Add nested assets structure if missing
                    if 'assets' not in report_data.get('balance_sheet', {}):
                        report_data['balance_sheet']['assets'] = {
                            'current_assets': [],
                            'non_current_assets': []
                        }
                    # Add nested liabilities structure if missing
                    if 'liabilities' not in report_data.get('balance_sheet', {}):
                        report_data['balance_sheet']['liabilities'] = {
                            'current_liabilities': [],
                            'long_term_liabilities': []
                        }
                    # Add total values if missing
                    if 'total_assets' not in report_data.get('balance_sheet', {}):
                        report_data['balance_sheet']['total_assets'] = 0
                    if 'total_liabilities' not in report_data.get('balance_sheet', {}):
                        report_data['balance_sheet']['total_liabilities'] = 0
                    # Add ratios field if missing
                    if 'ratios' not in report_data:
                        report_data['ratios'] = {}
                    # Add insights and recommendations if missing
                    if 'insights' not in report_data:
                        report_data['insights'] = ["Balance sheet analysis is pending."]
                    if 'recommendations' not in report_data:
                        report_data['recommendations'] = ["Review your balance sheet for further insights."]
                        
                elif report_type == 'income_statement':
                    # Add income_statement field if missing
                    if 'income_statement' not in report_data:
                        report_data['income_statement'] = {}
                    # Add revenue and other required fields
                    for field in ['revenue', 'expenses', 'net_income']:
                        if field not in report_data.get('income_statement', {}):
                            report_data['income_statement'][field] = 0
                    # Add insights and recommendations if missing
                    if 'insights' not in report_data:
                        report_data['insights'] = ["Income statement analysis is pending."]
                    if 'recommendations' not in report_data:
                        report_data['recommendations'] = ["Review your income statement for further insights."]
                
                # Save report to database - safely handle JSON serialization
                try:
                    json_data = json.dumps(report_data)
                except Exception as json_error:
                    logger.error(f"JSON encoding error: {str(json_error)}")
                    json_data = '{}'  # Use empty dict if serialization fails
                
                report = Report(
                    report_type=report_type,
                    data=json_data,
                    user_id=current_user.id,
                    file_id=file_id
                )
                db.session.add(report)
                db.session.commit()
                
                # Add IST datetime for all templates
                return render_template(template, report=report, data=report_data, ist_datetime=format_ist_time())
            except Exception as report_error:
                import traceback
                logger.error(f"Error generating specific report: {str(report_error)}")
                logger.error(traceback.format_exc())
                # Use fallback data for the report
                report_data = {}
                # Create report with empty data
                report = Report(
                    report_type=report_type,
                    data='{}',
                    user_id=current_user.id,
                    file_id=file_id
                )
                db.session.add(report)
                db.session.commit()
                
                if report_type == 'analysis':
                    template = 'financial_analysis.html'
                    return render_template(template, report=report, data={}, ist_datetime=format_ist_time())
                else:
                    flash(f'Error generating report: {str(report_error)}', 'danger')
                    return redirect(url_for('report_options'))
        
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
        import logging
        logger = logging.getLogger('fintelligence')
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to view this report.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Safely parse JSON data
        try:
            report_data = json.loads(report.data)
            # Ensure it's a dict to prevent template errors
            if not isinstance(report_data, dict):
                report_data = {}
                
            # Add required fields if missing for specific report types
            if report.report_type == 'cash_flow':
                # Add metrics field if missing
                if 'metrics' not in report_data:
                    report_data['metrics'] = {}
                # Add cash_flow_statement field if missing
                if 'cash_flow_statement' not in report_data:
                    report_data['cash_flow_statement'] = {}
                # Add insights and recommendations if missing
                if 'insights' not in report_data:
                    report_data['insights'] = ["Analysis of cash flow patterns is pending."]
                if 'recommendations' not in report_data:
                    report_data['recommendations'] = ["Review your cash flow statement for further insights."]
                    
            elif report.report_type == 'balance_sheet':
                # Add balance_sheet field if missing
                if 'balance_sheet' not in report_data:
                    report_data['balance_sheet'] = {}
                # Add nested assets structure if missing
                if 'assets' not in report_data.get('balance_sheet', {}):
                    report_data['balance_sheet']['assets'] = {
                        'current_assets': [],
                        'non_current_assets': []
                    }
                # Add nested liabilities structure if missing
                if 'liabilities' not in report_data.get('balance_sheet', {}):
                    report_data['balance_sheet']['liabilities'] = {
                        'current_liabilities': [],
                        'long_term_liabilities': []
                    }
                # Add total values if missing
                if 'total_assets' not in report_data.get('balance_sheet', {}):
                    report_data['balance_sheet']['total_assets'] = 0
                if 'total_liabilities' not in report_data.get('balance_sheet', {}):
                    report_data['balance_sheet']['total_liabilities'] = 0
                # Add ratios field if missing
                if 'ratios' not in report_data:
                    report_data['ratios'] = {}
                # Add insights and recommendations if missing
                if 'insights' not in report_data:
                    report_data['insights'] = ["Balance sheet analysis is pending."]
                if 'recommendations' not in report_data:
                    report_data['recommendations'] = ["Review your balance sheet for further insights."]
                    
            elif report.report_type == 'income_statement':
                # Add income_statement field if missing
                if 'income_statement' not in report_data:
                    report_data['income_statement'] = {}
                # Add revenue and other required fields
                for field in ['revenue', 'expenses', 'net_income']:
                    if field not in report_data.get('income_statement', {}):
                        report_data['income_statement'][field] = 0
                # Add ratios field if missing
                if 'ratios' not in report_data:
                    report_data['ratios'] = {}
                # Add insights and recommendations if missing
                if 'insights' not in report_data:
                    report_data['insights'] = ["Income statement analysis is pending."]
                if 'recommendations' not in report_data:
                    report_data['recommendations'] = ["Review your income statement for further insights."]
                    
        except Exception as e:
            logger.error(f"Error parsing report data JSON: {str(e)}")
            report_data = {}  # Use empty dict on error
        
        if report.report_type == 'balance_sheet':
            template = 'balance_sheet.html'
        elif report.report_type == 'income_statement':
            template = 'income_statement.html'
        elif report.report_type == 'cash_flow':
            template = 'cash_flow.html'
        elif report.report_type == 'analysis':
            template = 'financial_analysis.html'
        else:
            flash('Invalid report type.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Generate dynamic quarters for fallback data
        def generate_fallback_quarters():
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            quarters = []
            if current_month >= 1: quarters.append(f"Q1 {current_year}")  # Jan-Mar
            if current_month >= 4: quarters.append(f"Q2 {current_year}")  # Apr-Jun
            if current_month >= 7: quarters.append(f"Q3 {current_year}")  # Jul-Sep
            if current_month >= 10: quarters.append(f"Q4 {current_year}")  # Oct-Dec
            
            # Ensure we have at least one quarter
            if not quarters:
                quarters.append(f"Q1 {current_year}")
            
            return quarters
        
        # Get fallback quarters
        fallback_quarters = generate_fallback_quarters()
        
        # Check if print mode is enabled (for PDF download)
        print_mode = request.args.get('print_mode', '0') == '1'
        
        # Add IST datetime and fallback quarters for all templates
        html_content = render_template(
            template, 
            report=report, 
            data=report_data, 
            ist_datetime=format_ist_time(),
            fallback_quarters=fallback_quarters,
            print_mode=print_mode
        )
        
        # If in print mode, add a script to trigger print dialog when page loads
        if print_mode:
            script = """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Small delay to ensure everything is loaded
                    setTimeout(function() {
                        window.print();
                    }, 500);
                });
            </script>
            """
            # Insert script before closing body tag
            html_content = html_content.replace('</body>', script + '</body>')
            
        return html_content
    
    @app.route('/download-report/<int:report_id>')
    @login_required
    def download_report(report_id):
        """Redirect to the PDF download route."""
        return redirect(url_for('download_report_pdf', report_id=report_id))
        
    @app.route('/delete-report/<int:report_id>', methods=['POST'])
    @login_required
    def delete_report(report_id):
        """Delete a report from the database."""
        report = Report.query.get_or_404(report_id)
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to delete this report.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get the file_id before deleting for redirection
        file_id = report.file_id
        
        # Delete the report
        db.session.delete(report)
        db.session.commit()
        
        flash('Report deleted successfully.', 'success')
        return redirect(url_for('report_options', file_id=file_id))
    
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
            import logging
            logger = logging.getLogger('fintelligence')
            
            try:
                user_files = FileUpload.query.filter_by(user_id=current_user.id, processed=True).all()
                file_data = []
                
                for file in user_files:
                    reports = Report.query.filter_by(file_id=file.id).all()
                    if reports:
                        for report in reports:
                            try:
                                report_json = json.loads(report.data)
                                if not isinstance(report_json, dict):
                                    report_json = {}
                            except Exception as json_error:
                                logger.error(f"Error parsing report JSON for chatbot: {str(json_error)}")
                                report_json = {}
                                
                            file_data.append({
                                'filename': file.filename,
                                'report_type': report.report_type,
                                'data': report_json
                            })
                
                ai_response = process_chat_query(user_message, file_data)
            except Exception as e:
                import traceback
                logger.error(f"Error processing chat query: {str(e)}")
                logger.error(traceback.format_exc())
                ai_response = "I'm sorry, I encountered an error while processing your question. Please try again with a more specific query about your financial data."
            
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
        import logging
        logger = logging.getLogger('fintelligence')
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to view this explanation.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Safely parse JSON data
        try:
            report_data = json.loads(report.data)
            # Ensure it's a dict to prevent errors
            if not isinstance(report_data, dict):
                report_data = {}
        except Exception as e:
            logger.error(f"Error parsing report data JSON for explanation: {str(e)}")
            report_data = {}  # Use empty dict on error
        
        try:
            explanation = explain_ai_decision(report.report_type, report_data)
        except Exception as e:
            import traceback
            logger.error(f"Error generating AI explanation: {str(e)}")
            logger.error(traceback.format_exc())
            explanation = {
                "process": "The AI model encountered issues while explaining this report.",
                "factors": ["Data structure might be incomplete", "Some keys might be missing in the data"],
                "alternatives": ["Try regenerating the report", "Upload more detailed financial data"]
            }
        
        return render_template('explainability.html', report=report, explanation=explanation)
        
    @app.route('/demo-analysis')
    @login_required
    def demo_analysis():
        """Redirect to upload page with a message about using real data."""
        flash('Demo analysis has been replaced with real data analysis. Please upload your financial data to generate accurate reports.', 'info')
        return redirect(url_for('upload'))
        
    @app.route('/download-report-pdf/<int:report_id>')
    @login_required
    def download_report_pdf(report_id):
        """Download a report directly as a print-friendly webpage."""
        report = Report.query.get_or_404(report_id)
        import logging
        logger = logging.getLogger('fintelligence')
        
        # Ensure the report belongs to the current user
        if report.user_id != current_user.id:
            flash('You do not have permission to download this report.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Simply redirect to the view_report page with a print parameter
        # This will trigger browser's print dialog when the page loads
        return redirect(url_for('view_report', report_id=report.id, print_mode=1))
