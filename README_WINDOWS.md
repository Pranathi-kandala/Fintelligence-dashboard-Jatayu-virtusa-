# Running Fintelligence Locally on Windows

This guide will help you set up and run the Fintelligence application on your Windows machine.

## Prerequisites

1. Python 3.10 or higher installed 
   - [Download from python.org](https://www.python.org/downloads/windows/)
   - Make sure to check "Add Python to PATH" during installation

2. PostgreSQL installed (recommended) or SQLite (simpler but less powerful)
   - [Download PostgreSQL for Windows](https://www.postgresql.org/download/windows/)
   - Note your superuser username and password during installation

3. Git (optional, for downloading the code)
   - [Download Git for Windows](https://git-scm.com/download/win)

## Step 1: Download the Code

Either download a ZIP file of the project or clone it using Git:

```bash
git clone https://your-repository-url.git
cd fintelligence
```

## Step 2: Set Up a Virtual Environment

Open Command Prompt or PowerShell and run:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Install python-dotenv first for .env file support
pip install python-dotenv

# Install all required packages
pip install -r requirements_local.txt
```

## Step 4: Set Up the Database

### Option 1: Use PostgreSQL (Recommended)

Run the helper script:

```bash
python create_windows_db.py
```

This will:
1. Check if PostgreSQL is installed
2. Ask for your PostgreSQL superuser credentials
3. Create a new database and user for Fintelligence
4. Update your .env file with the database connection string

### Option 2: Use SQLite (Simpler)

Create a `.env` file in the project root with:

```
# Use SQLite (the application will default to this if DATABASE_URL is not set)
# GEMINI API key (required for chatbot)
GEMINI_API_KEY=your_gemini_api_key
# Flask secret key (for session security)
SECRET_KEY=your_secret_key_here
```

## Step 5: Complete Environment Setup

Make sure your `.env` file contains:

```
# Database connection (if using PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/fintelligence

# Gemini API key (required for chatbot)
GEMINI_API_KEY=your_gemini_api_key

# Flask secret key (for session security)
SECRET_KEY=your_secret_key_here
```

## Step 6: Run the Application

Run the application using the helper script:

```bash
python run_locally.py
```

This will:
1. Check that all requirements are installed
2. Verify your environment variables
3. Set up the database tables if needed
4. Start the Flask development server

## Step 7: Access the Application

Open your browser and navigate to:

```
http://localhost:5000
```

## Troubleshooting

### Database Connections
- For PostgreSQL, make sure the PostgreSQL service is running
- Check your database credentials in the .env file

### Missing Packages
- Make sure your virtual environment is activated
- Try installing any missing package: `pip install package_name`

### File Permissions
- Make sure your user account has write permissions to the project directory

### Gemini API Key Issues
- If you encounter quota limit errors, create a new API key or try again later

## Additional Notes

- The first time you run the application, it will create all necessary database tables
- For production use, consider using a more robust WSGI server like gunicorn