"""
Script to fix file upload issues on Windows
"""
import os
import sys
import shutil
from pathlib import Path

def create_temp_directory():
    """Ensure the temp directory exists and has the correct permissions"""
    print("Creating and fixing temp directory...")
    
    # Get the project root directory
    root_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Define paths for temp and uploads directories
    temp_dir = os.path.join(root_dir, 'temp')
    uploads_dir = os.path.join(root_dir, 'uploads')
    
    # Create directories if they don't exist
    for directory in [temp_dir, uploads_dir]:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✓ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Error creating directory {directory}: {e}")
                return False
        else:
            # Clean out existing temp files to prevent conflicts
            if directory == temp_dir:
                try:
                    for item in os.listdir(directory):
                        item_path = os.path.join(directory, item)
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                    print(f"✓ Cleaned temp directory: {directory}")
                except Exception as e:
                    print(f"❌ Error cleaning temp directory: {e}")
        
        # Test write permissions
        test_file = os.path.join(directory, "test_write.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("Test file write permission")
            os.unlink(test_file)
            print(f"✓ Directory has write permissions: {directory}")
        except Exception as e:
            print(f"❌ Cannot write to directory {directory}: {e}")
            return False
    
    # Make sure sample data is available in the attached_assets directory
    sample_source = os.path.join(root_dir, 'attached_assets', 'Updated_Realistic_Financial_Data.csv')
    sample_dest = os.path.join(root_dir, 'Updated_Realistic_Financial_Data.csv')
    
    if os.path.exists(sample_source) and not os.path.exists(sample_dest):
        try:
            shutil.copy(sample_source, sample_dest)
            print(f"✓ Copied sample data file to root directory")
        except Exception as e:
            print(f"❌ Could not copy sample data: {e}")
    
    return True

def fix_routes_file():
    """Fix the file path handling in routes.py"""
    routes_file = "routes.py"
    
    if not os.path.exists(routes_file):
        print(f"❌ Could not find {routes_file}")
        return False
    
    with open(routes_file, 'r') as f:
        content = f.read()
    
    # Replace file path handling code to use platform-independent paths
    replacements = [
        (
            "os.remove(temp_path)",
            "try:\n                os.remove(temp_path)\n            except FileNotFoundError:\n                # It's okay if the file is already gone\n                pass"
        ),
        (
            "temp_path = os.path.join('temp', secure_filename(file.filename))",
            "temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', secure_filename(file.filename))"
        ),
        (
            "file_path = os.path.join('uploads', secure_filename(file.filename))",
            "file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', secure_filename(file.filename))"
        )
    ]
    
    modified = False
    new_content = content
    
    for old, new in replacements:
        if old in new_content:
            new_content = new_content.replace(old, new)
            modified = True
    
    if modified:
        with open(routes_file, 'w') as f:
            f.write(new_content)
        print(f"✓ Fixed file path handling in {routes_file}")
    else:
        print(f"✓ No changes needed in {routes_file}")
    
    return True

if __name__ == "__main__":
    print("Fixing File Upload Issues for Windows")
    print("====================================")
    
    if create_temp_directory() and fix_routes_file():
        print("\n✓ All fixes applied successfully!")
        print("\nTry uploading your file again. It should work now.")
    else:
        print("\n❌ Some fixes could not be applied.")
        print("Please check the error messages above.")