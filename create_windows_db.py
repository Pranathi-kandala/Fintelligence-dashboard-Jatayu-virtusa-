"""
Script to help set up a PostgreSQL database for Fintelligence on Windows
"""
import os
import sys
import getpass
import subprocess
import psycopg2
from psycopg2 import sql

def check_psql_installation():
    """Check if PostgreSQL is installed"""
    try:
        subprocess.run(['psql', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_database_credentials():
    """Get database credentials from user"""
    print("\nPlease provide your PostgreSQL credentials:")
    host = input("Host [localhost]: ") or "localhost"
    port = input("Port [5432]: ") or "5432"
    superuser = input("Superuser name [postgres]: ") or "postgres"
    password = getpass.getpass("Superuser password: ")
    
    return host, port, superuser, password

def create_database_and_user(host, port, superuser, password):
    """Create the database and user"""
    db_name = input("\nDatabase name [fintelligence]: ") or "fintelligence"
    user_name = input("Application user name [fintelligence_user]: ") or "fintelligence_user"
    user_password = getpass.getpass("Application user password: ")
    
    # Connect to PostgreSQL as superuser
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=superuser,
            password=password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        else:
            print(f"Database '{db_name}' already exists.")
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (user_name,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            print(f"Creating user '{user_name}'...")
            cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                sql.Identifier(user_name)), (user_password,))
        else:
            print(f"User '{user_name}' already exists. Updating password...")
            cursor.execute(sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                sql.Identifier(user_name)), (user_password,))
        
        # Grant privileges
        print(f"Granting privileges on '{db_name}' to '{user_name}'...")
        cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(db_name), sql.Identifier(user_name)))
        
        # Connect to the new database to set permissions on schema
        conn.close()
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=superuser,
            password=password,
            database=db_name
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Grant schema permissions
        cursor.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
            sql.Identifier(user_name)))
        
        conn.close()
        
        # Generate DATABASE_URL
        db_url = f"postgresql://{user_name}:{user_password}@{host}:{port}/{db_name}"
        return db_url
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

def update_env_file(db_url):
    """Update or create .env file with the database URL"""
    try:
        env_file = '.env'
        
        # Check if .env file exists
        if os.path.exists(env_file):
            # Read existing content
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update or add DATABASE_URL
            db_url_found = False
            with open(env_file, 'w') as f:
                for line in lines:
                    if line.startswith('DATABASE_URL='):
                        f.write(f'DATABASE_URL={db_url}\n')
                        db_url_found = True
                    else:
                        f.write(line)
                
                if not db_url_found:
                    f.write(f'\nDATABASE_URL={db_url}\n')
        else:
            # Create new .env file
            with open(env_file, 'w') as f:
                f.write(f'DATABASE_URL={db_url}\n')
                f.write('# Add your GEMINI_API_KEY below\n')
                f.write('GEMINI_API_KEY=your_gemini_api_key\n')
                f.write('# Add a secret key for Flask\n')
                f.write('SECRET_KEY=your_secret_key_here\n')
        
        print(f"\n✓ Database URL saved to {env_file}")
        
    except Exception as e:
        print(f"Error updating .env file: {e}")
        print(f"\nPlease add the following line to your .env file manually:")
        print(f"DATABASE_URL={db_url}")

if __name__ == "__main__":
    print("Fintelligence - PostgreSQL Database Setup for Windows")
    print("===================================================")
    
    if not check_psql_installation():
        print("❌ PostgreSQL is not installed or not in your PATH.")
        print("Please install PostgreSQL from https://www.postgresql.org/download/windows/")
        sys.exit(1)
    
    print("✓ PostgreSQL is installed")
    
    host, port, superuser, password = get_database_credentials()
    db_url = create_database_and_user(host, port, superuser, password)
    update_env_file(db_url)
    
    print("\nDatabase setup complete!")
    print("\nNext steps:")
    print("1. Update your .env file with your GEMINI_API_KEY")
    print("2. Run 'python run_locally.py' to start the application")