This script automates the workflow for Checkmarx scanning, report generation, and emailing scan results. It is a Python-based solution that uses the Checkmarx CLI to interact with Checkmarx services.

## Prerequisites

1. **Python 3.x** installed on your system.
2. **Checkmarx CLI** (`cx`) installed and accessible via the CLI
3. Generate a valid **Checkmarx API key**.
4. **Git** installed to clone repositories.
5. SMTP server credentials for sending emails

## Features

- Configures the Checkmarx API key.
- Lists and manages Checkmarx projects.
- Initiates scans for specified projects and branches.
- Generates scan reports in **JSON** and **SARIF** formats.
- Sends email notifications with scan reports as attachments.

## Configuration

Update the following variables in the script as per your requirements:

- **CLI_PATH**: Path to the Checkmarx CLI binary.
- **WORKING_DIR**: Directory where the script operates.
- **SMTP_SERVER**, **SMTP_PORT**: SMTP server details for email.
- **SENDER_EMAIL**, **SENDER_PASSWORD**: Email credentials for sending emails.
- **RECIPIENT_EMAIL**: The recipient's email address.

## Usage Instructions

1. Clone the repository where the script resides and navigate to the directory.
    
2. Run the script using:
3. Follow the on-screen prompts:
    - Enter your **Checkmarx API Key**.
    - Provide the **Project Name** and **Branch Name**.
    - Provide the **GitHub repository URL** for the source code to scan.
4. - The script will:
    
    - Check if the project exists in Checkmarx and create it if necessary.
    - Clone the GitHub repository if not already cloned.
    - Initiate a scan for the specified project.
    - Generate **JSON** and **SARIF** scan reports.
    - Send an email with the scan reports attached.


## Error Handling

- If a command fails, the script will print an error message and terminate.
- Ensure correct permissions and valid inputs to avoid runtime errors.

## Notes

- Use secure methods to manage sensitive data (e.g., API keys and passwords).
- Customize paths and configurations according to your environment.