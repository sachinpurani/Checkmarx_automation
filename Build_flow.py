import os
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configuration
CLI_PATH = "/usr/local/bin/cx"
WORKING_DIR = "/home/sachinpurani/Documents/Checkmarx"

# Email Configuration
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_email_password"
SMTP_SERVER = "smtp.gmail.com"  # Replace with your email provider's SMTP server
SMTP_PORT = 587  # Usually 587 for TLS
RECIPIENT_EMAIL = "recipient_email@example.com"  # The recipient's email

def run_command(command, cwd=None):
    """
    Utility function to execute shell commands and capture output.
    """
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {command}\nError: {result.stderr}")
    return result.stdout.strip()

def set_api_key(api_key):
    """
    Sets the API key for Checkmarx CLI.
    """
    print("Configuring API key...")
    command = f"{CLI_PATH} configure set api-key {api_key}"
    run_command(command)
    print("API key configured successfully.")

def list_projects():
    """
    Lists all projects in Checkmarx.
    """
    print("Listing all projects...")
    command = f"{CLI_PATH} project list"
    return run_command(command)

def project_exists(project_name):
    """
    Checks if a project already exists.
    """
    print(f"Checking if project '{project_name}' already exists...")
    projects = list_projects()
    if project_name in projects:
        print(f"Project '{project_name}' already exists.")
        return True
    return False

def create_project(project_name):
    """
    Creates a new project using the Checkmarx CLI if it doesn't exist.
    """
    print(f"Creating project: {project_name}")
    command = f"{CLI_PATH} project create --project-name \"{project_name}\""
    try:
        output = run_command(command)
        print(output)
    except RuntimeError as e:
        if 'already exists' in str(e):
            print(f"Project '{project_name}' already exists. Skipping project creation.")
        else:
            raise e

def initiate_scan(project_name, branch_name, source_path):
    """
    Initiates a scan for the specified project.
    """
    print(f"Initiating scan for project: {project_name}")
    command = (
        f"{CLI_PATH} scan create --project-name \"{project_name}\" "
        f"-s \"{source_path}\" --branch \"{branch_name}\" "
        "--scan-types sast --report-format json --output-name scan-report.json"
    )
    output = run_command(command)
    print(output)

def list_scans():
    """
    Lists all scans to verify scan initiation.
    """
    print("Retrieving scan list...")
    command = f"{CLI_PATH} scan list"
    return run_command(command)

def generate_scan_results(scan_id):
    """
    Retrieves scan results and generates reports in JSON and SARIF formats.
    """
    print(f"Retrieving scan results for Scan ID: {scan_id}")
    
    # Generate JSON report
    command = f"{CLI_PATH} results show --scan-id {scan_id} --report-format json --output-name cx_result --output-path \"{WORKING_DIR}\""
    run_command(command)
    json_file = os.path.join(WORKING_DIR, "cx_result.json")
    print(f"JSON report generated at: {json_file}")
    
    # Generate SARIF report
    command = f"{CLI_PATH} results show --scan-id {scan_id} --report-format sarif --output-name Demo --output-path \"{WORKING_DIR}\""
    run_command(command)
    sarif_file = os.path.join(WORKING_DIR, "Demo.sarif")
    print(f"SARIF report generated at: {sarif_file}")

    return [json_file, sarif_file]

def send_email_with_attachments(subject, body, attachments):
    """
    Send an email with attachments using Gmail's SMTP server.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEBase('text', 'plain'))
        msg.get_payload()[0].set_payload(body)

        # Attach files
        for file_path in attachments:
            part = MIMEBase('application', 'octet-stream')
            with open(file_path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            msg.attach(part)

        print("Connecting to the SMTP server...")
        # Use TLS with SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
            print(f"Email sent successfully to {RECIPIENT_EMAIL}!")
    except Exception as e:
        print(f"Error sending email: {e}")





def main():
    try:
        print("Welcome to the Checkmarx Workflow Script!")
        os.chdir(WORKING_DIR)

        # Prompt for API Key
        api_key = input("Enter your Checkmarx API Key: ").strip()
        set_api_key(api_key)

        # Prompt for Project Name and Branch
        project_name = input("Enter the project name: ").strip()
        branch_name = input("Enter the branch name (e.g., 'main' or 'master'): ").strip()

        # Check if the project already exists
        if not project_exists(project_name):
            # If the project doesn't exist, create it
            create_project(project_name)

        # Always prompt for the GitHub repository URL and clone it (even if the directory already exists)
        source_path = "./vulnerable-project"
        repo_url = input("Enter the GitHub repository URL to clone (this will be used for every scan): ").strip()
        if not os.path.exists(source_path):
            print(f"Directory '{source_path}' not found. Cloning the repository...")
            clone_command = f"git clone {repo_url} {source_path}"
            run_command(clone_command)
            print(f"Repository cloned at: {source_path}")
        else:
            print(f"Directory '{source_path}' already exists, using existing repository from: {source_path}")

        # Initiate a scan
        initiate_scan(project_name, branch_name, source_path)

        # Verify scan initiation
        scans = list_scans()
        scan_id = None
        for line in scans.split("\n"):
            if project_name in line:
                scan_id = line.split()[0]  # Extract Scan ID
                break
        if not scan_id:
            raise RuntimeError(f"No scan found for project '{project_name}'.")

        # Generate results and reports
        attachments = generate_scan_results(scan_id)

        # Send email with attachments
        email_subject = f"Checkmarx Scan Report for {project_name}"
        email_body = "Attached are the scan reports in JSON and SARIF formats."
        send_email_with_attachments(email_subject, email_body, attachments)

        print("Workflow completed successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
