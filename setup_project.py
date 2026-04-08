import os
import subprocess
import sys

def run_command(command):
    print(f"Executing: {command}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False
    return True

def setup():
    print("=== Legal Red Line: Project Setup ===")
    
    # 1. Install dependencies
    print("\n[1/3] Installing dependencies...")
    run_command("pip install -r requirements.txt python-dotenv")
    
    # 2. Check for .env file
    print("\n[2/3] Checking for API configuration...")
    if not os.path.exists(".env"):
        print("No .env file found. Creating a template...")
        with open(".env", "w") as f:
            f.write("# Replace with your actual key\nHF_TOKEN=\"your_api_key_here\"\n")
        print("!!! ACTION REQUIRED: Open the '.env' file and paste your OpenAI or HuggingFace API key.")
    else:
        print(".env file already exists.")
        
    # 3. Final Verification
    print("\n[3/3] Verifying environment logic...")
    print("Running a mock test to ensure everything is configured correctly...")
    run_command("python3 mock_inference.py")
    
    print("\n=== Setup Complete! ===")
    print("Once you have updated your .env file, run the real benchmark with:")
    print("python3 inference.py")

if __name__ == "__main__":
    setup()
