#!/bin/bash
# secure_aws_setup.sh - Set up secure AWS credentials for the Quantum Consciousness System

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}${BLUE}Secure AWS Credentials Setup${NC}\n"
echo -e "${YELLOW}This script will set up AWS credentials securely for your application.${NC}\n"

# Create AWS config directory if it doesn't exist
AWS_DIR="$HOME/.aws"
if [ ! -d "$AWS_DIR" ]; then
    echo -e "${BOLD}Creating AWS configuration directory...${NC}"
    mkdir -p "$AWS_DIR"
    chmod 700 "$AWS_DIR"
    echo -e "${GREEN}✓ Created $AWS_DIR${NC}\n"
fi

# Function to securely set up credentials
setup_aws_credentials() {
    echo -e "${BOLD}Setting up AWS credentials securely...${NC}"
    
    # Create credentials file with restricted permissions
    CRED_FILE="$AWS_DIR/credentials"
    
    # Check if file exists and back it up if it does
    if [ -f "$CRED_FILE" ]; then
        echo -e "${YELLOW}Existing credentials file found, creating backup...${NC}"
        cp "$CRED_FILE" "$CRED_FILE.bak.$(date +%Y%m%d%H%M%S)"
    fi
    
    # Create new credentials file with secure permissions
    touch "$CRED_FILE"
    chmod 600 "$CRED_FILE"
    
    # Use AWS CLI to set credentials securely (safer than editing the file directly)
    echo -e "${BOLD}Setting up 'quantum-consciousness' profile...${NC}"
    aws configure set aws_access_key_id "YOUR_ACCESS_KEY" --profile quantum-consciousness
    aws configure set aws_secret_access_key "YOUR_SECRET_KEY" --profile quantum-consciousness
    aws configure set region "us-east-1" --profile quantum-consciousness
    
    echo -e "${GREEN}✓ AWS credentials securely configured${NC}\n"
    echo -e "${YELLOW}IMPORTANT: Replace the placeholder credentials with your actual keys using:${NC}"
    echo -e "${YELLOW}aws configure --profile quantum-consciousness${NC}\n"
}

# Update the application config to use AWS profile
update_app_config() {
    CONFIG_DIR="$HOME/quantum-consciousness"
    ENV_FILE="$CONFIG_DIR/.env"
    
    echo -e "${BOLD}Updating application configuration...${NC}"
    
    # Ensure the application directory exists
    if [ ! -d "$CONFIG_DIR" ]; then
        echo -e "${RED}Error: Quantum Consciousness directory not found at $CONFIG_DIR${NC}"
        echo -e "${YELLOW}Please run the main setup script first.${NC}"
        exit 1
    fi
    
    # Update or add AWS configuration
    if [ -f "$ENV_FILE" ]; then
        # Remove any existing AWS credential lines for security
        sed -i '/AWS_ACCESS_KEY/d' "$ENV_FILE"
        sed -i '/AWS_SECRET_KEY/d' "$ENV_FILE"
        sed -i '/AWS_PROFILE/d' "$ENV_FILE"
        
        # Add AWS profile configuration
        echo "" >> "$ENV_FILE"
        echo "# AWS Configuration" >> "$ENV_FILE"
        echo "AWS_PROFILE=quantum-consciousness" >> "$ENV_FILE"
        echo "AWS_REGION=us-east-1" >> "$ENV_FILE"
        
        echo -e "${GREEN}✓ Application configuration updated to use AWS profile${NC}\n"
    else
        echo -e "${RED}Error: .env file not found at $ENV_FILE${NC}"
        exit 1
    fi
}

# Create AWS credential usage module
create_aws_module() {
    CONFIG_DIR="$HOME/quantum-consciousness"
    MODULE_FILE="$CONFIG_DIR/aws_helper.py"
    
    echo -e "${BOLD}Creating secure AWS helper module...${NC}"
    
    cat > "$MODULE_FILE" << 'EOL'
#!/usr/bin/env python3
"""
aws_helper.py - Secure AWS integration for Quantum Consciousness System
This module safely handles AWS credentials and provides helper functions
for AWS services integration.
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("quantum-consciousness-aws")

class AWSHelper:
    """Helper class for AWS operations with secure credential handling"""
    
    def __init__(self):
        """Initialize AWS helper with profile from environment"""
        self.profile_name = os.getenv('AWS_PROFILE', 'quantum-consciousness')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.session = None
        self.s3_client = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize AWS session using profile credentials"""
        try:
            # Create session from profile - secure way to handle credentials
            self.session = boto3.Session(profile_name=self.profile_name, region_name=self.region)
            logger.info(f"AWS session initialized using profile '{self.profile_name}'")
        except ClientError as e:
            logger.error(f"Failed to initialize AWS session: {str(e)}")
            raise
    
    def get_s3_client(self):
        """Get or create S3 client"""
        if not self.s3_client:
            if not self.session:
                self._initialize_session()
            self.s3_client = self.session.client('s3')
        return self.s3_client
    
    def upload_file(self, file_path, bucket, object_name=None):
        """Upload a file to S3 bucket
        
        Args:
            file_path (str): Path to the file to upload
            bucket (str): S3 bucket name
            object_name (str, optional): S3 object name. If not specified, file_path is used.
            
        Returns:
            bool: True if file was uploaded, else False
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        s3_client = self.get_s3_client()
        try:
            s3_client.upload_file(file_path, bucket, object_name)
            logger.info(f"Successfully uploaded {file_path} to s3://{bucket}/{object_name}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return False
    
    def download_file(self, bucket, object_name, file_path):
        """Download a file from S3 bucket
        
        Args:
            bucket (str): S3 bucket name
            object_name (str): S3 object name
            file_path (str): Path where the file should be saved
            
        Returns:
            bool: True if file was downloaded, else False
        """
        s3_client = self.get_s3_client()
        try:
            s3_client.download_file(bucket, object_name, file_path)
            logger.info(f"Successfully downloaded s3://{bucket}/{object_name} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            return False
    
    def list_buckets(self):
        """List all S3 buckets
        
        Returns:
            list: List of bucket names
        """
        s3_client = self.get_s3_client()
        try:
            response = s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            return buckets
        except ClientError as e:
            logger.error(f"Error listing S3 buckets: {str(e)}")
            return []


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the AWS helper
    try:
        aws = AWSHelper()
        buckets = aws.list_buckets()
        print(f"Available S3 buckets: {buckets}")
    except Exception as e:
        print(f"Error: {str(e)}")
EOL

    chmod +x "$MODULE_FILE"
    echo -e "${GREEN}✓ AWS helper module created at $MODULE_FILE${NC}\n"
}

# Update application launch script
update_launch_script() {
    CONFIG_DIR="$HOME/quantum-consciousness"
    LAUNCH_SCRIPT="$CONFIG_DIR/launch_server.py"
    
    echo -e "${BOLD}Updating launch script with AWS integration...${NC}"
    
    if [ -f "$LAUNCH_SCRIPT" ]; then
        # Add AWS import at the top of the file
        sed -i '1s/^/# AWS integration added\n/' "$LAUNCH_SCRIPT"
        sed -i '/import logging/a import os\nfrom aws_helper import AWSHelper' "$LAUNCH_SCRIPT"
        
        # Initialize AWS helper in the main function
        sed -i '/def main/a \ \ \ \ # Initialize AWS helper if AWS profile is configured\n    if os.getenv("AWS_PROFILE"):\n        try:\n            aws_helper = AWSHelper()\n            logger.info(f"AWS integration initialized with profile {os.getenv(\\"AWS_PROFILE\\")}")\n        except Exception as e:\n            logger.warning(f"AWS integration initialization failed: {str(e)}")' "$LAUNCH_SCRIPT"
        
        echo -e "${GREEN}✓ Launch script updated with AWS integration${NC}\n"
    else
        echo -e "${RED}Error: Launch script not found at $LAUNCH_SCRIPT${NC}"
    fi
}

# Run the setup functions
setup_aws_credentials
update_app_config
create_aws_module
update_launch_script

echo -e "${BOLD}${GREEN}AWS Integration Setup Complete!${NC}\n"
echo -e "${YELLOW}IMPORTANT: You need to update your actual AWS credentials by running:${NC}"
echo -e "${BOLD}aws configure --profile quantum-consciousness${NC}\n"
echo -e "This setup allows your application to use AWS credentials securely without embedding them in code."
echo -e "The AWS_PROFILE environment variable will direct the application to use your credentials securely."
