# Running Fintelligence Locally on Windows

This guide will help you set up and run the Fintelligence application on your Windows machine.

## Windows Compatibility

This application has been specially adapted to work seamlessly on Windows by:

1. Using cross-platform file paths with `os.path.join()` instead of hard-coded Unix paths
2. Creating application-specific temp and uploads directories instead of using the system temp folder
3. Supporting path normalization to handle both forward slashes (/) and backslashes (\)
4. Adding dotenv support for easier environment variable management
5. Using relative paths for database connections to support SQLite as a fallback

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

Run the database setup helper script:

```bash
python create_windows_db.py
```

This script gives you three options:

### Option 1: Local PostgreSQL (Recommended for Production)

If you choose local PostgreSQL, the script will:
1. Check if PostgreSQL is installed
2. Ask for your PostgreSQL superuser credentials
3. Create a new database and user for Fintelligence
4. Update your `.env` file with the database connection string

### Option 2: SQLite (Simpler, No Configuration)

If you choose SQLite, the script will:
1. Create the necessary directory structure
2. Configure the application to use SQLite
3. Set up a template `.env` file

The SQLite database will be automatically created in the `instance` folder when you first run the application. This option requires no additional database software.

### Option 3: Neon PostgreSQL (Cloud-hosted, No Local Installation)

If you choose Neon PostgreSQL, the script will:
1. Guide you through creating a Neon.tech account
2. Help you get your connection string from the Neon dashboard
3. Configure your application to use the Neon database

This option gives you a professional PostgreSQL database without requiring local installation. For detailed instructions on setting up Neon, see the `NEON_DB_SETUP.md` file.

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