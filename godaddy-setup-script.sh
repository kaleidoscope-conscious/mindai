#!/bin/bash
# setup_godaddy_domain.sh - Setup script for GoDaddy domain integration

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}${BLUE}GoDaddy Domain Setup for Quantum Consciousness System${NC}\n"
echo -e "${YELLOW}This script will set up your GoDaddy domain for use with the Quantum Consciousness System.${NC}\n"

# Define directory and files
INSTALL_DIR="$HOME/quantum-consciousness"
GODADDY_SCRIPT="$INSTALL_DIR/godaddy_manager.py"

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}Error: Quantum Consciousness installation directory not found at $INSTALL_DIR${NC}"
    echo -e "${YELLOW}Please run the main installation script first.${NC}"
    exit 1
fi

# Get GoDaddy credentials
echo -e "${BOLD}Enter your GoDaddy API credentials:${NC}"
read -p "API Key: " API_KEY
read -p "API Secret: " API_SECRET
read -p "Domain [artificialthinker.com]: " DOMAIN
DOMAIN=${DOMAIN:-artificialthinker.com}

# Create GoDaddy manager script
echo -e "\n${BOLD}Creating GoDaddy domain manager script...${NC}"

# Copy the godaddy_manager.py content here
cat > "$GODADDY_SCRIPT" << 'EOL'
#!/usr/bin/env python3
"""
godaddy_manager.py - Direct management of artificialthinker.com domain

This script provides functions to directly manage your GoDaddy domain,
including updating DNS records, checking domain status, and configuring
settings for the Quantum Consciousness System.
"""

import requests
import json
import os
import argparse
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("godaddy-manager")

# GoDaddy API configuration
class GoDaddyManager:
    """Manager for GoDaddy domain operations"""
    
    def __init__(self, domain: str, api_key: str, api_secret: str):
        """Initialize with domain and API credentials"""
        self.domain = domain
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = f"https://api.godaddy.com/v1/domains/{domain}"
        self.headers = {
            "Authorization": f"sso-key {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }
    
    def get_domain_info(self) -> Dict[str, Any]:
        """Get basic information about the domain"""
        try:
            response = requests.get(
                f"https://api.godaddy.com/v1/domains/{self.domain}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting domain info: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return {}
    
    def get_dns_records(self, record_type: str = None, name: str = None) -> List[Dict[str, Any]]:
        """Get DNS records for the domain"""
        url = f"{self.api_url}/records"
        
        # Add filters if specified
        params = {}
        if record_type:
            params['type'] = record_type
        if name:
            params['name'] = name
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting DNS records: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return []
    
    def update_dns_record(self, record_type: str, name: str, value: str, ttl: int = 600) -> bool:
        """Update a specific DNS record"""
        url = f"{self.api_url}/records/{record_type}/{name}"
        
        data = [{
            "data": value,
            "ttl": ttl
        }]
        
        try:
            logger.info(f"Updating {record_type} record for {name}.{self.domain} to {value}")
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            logger.info(f"Successfully updated DNS record")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating DNS record: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
    
    def add_dns_record(self, record_type: str, name: str, value: str, ttl: int = 600) -> bool:
        """Add a new DNS record"""
        url = f"{self.api_url}/records"
        
        data = [{
            "type": record_type,
            "name": name,
            "data": value,
            "ttl": ttl
        }]
        
        try:
            logger.info(f"Adding {record_type} record for {name}.{self.domain} with value {value}")
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            logger.info(f"Successfully added DNS record")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding DNS record: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
    
    def delete_dns_record(self, record_type: str, name: str) -> bool:
        """Delete a DNS record"""
        url = f"{self.api_url}/records/{record_type}/{name}"
        
        try:
            logger.info(f"Deleting {record_type} record for {name}.{self.domain}")
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Successfully deleted DNS record")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting DNS record: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
    
    def setup_quantum_subdomain(self, ip_address: str) -> bool:
        """Set up quantum.artificialthinker.com subdomain pointing to your server"""
        # First check if record exists
        records = self.get_dns_records(record_type="A", name="quantum")
        
        if records:
            # Update existing record
            return self.update_dns_record("A", "quantum", ip_address)
        else:
            # Create new record
            return self.add_dns_record("A", "quantum", ip_address)
    
    def setup_api_subdomain(self, ip_address: str) -> bool:
        """Set up api.artificialthinker.com subdomain pointing to your server"""
        # First check if record exists
        records = self.get_dns_records(record_type="A", name="api")
        
        if records:
            # Update existing record
            return self.update_dns_record("A", "api", ip_address)
        else:
            # Create new record
            return self.add_dns_record("A", "api", ip_address)
    
    def create_cname_record(self, subdomain: str, target: str) -> bool:
        """Create a CNAME record pointing a subdomain to a target domain"""
        # First check if record exists
        records = self.get_dns_records(record_type="CNAME", name=subdomain)
        
        if records:
            # Update existing record
            return self.update_dns_record("CNAME", subdomain, target)
        else:
            # Create new record
            return self.add_dns_record("CNAME", subdomain, target)

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Manage your GoDaddy domain")
    
    # Authentication arguments
    parser.add_argument("--key", help="GoDaddy API Key")
    parser.add_argument("--secret", help="GoDaddy API Secret")
    parser.add_argument("--domain", default="artificialthinker.com", help="Domain name to manage")
    
    # Command arguments
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get domain information")
    
    # List DNS records command
    list_parser = subparsers.add_parser("list", help="List DNS records")
    list_parser.add_argument("--type", help="Record type to filter by")
    list_parser.add_argument("--name", help="Record name to filter by")
    
    # Add/update DNS record command
    update_parser = subparsers.add_parser("update", help="Add or update a DNS record")
    update_parser.add_argument("--type", required=True, help="Record type")
    update_parser.add_argument("--name", required=True, help="Record name")
    update_parser.add_argument("--value", required=True, help="Record value/data")
    update_parser.add_argument("--ttl", type=int, default=600, help="Time to live in seconds")
    
    # Delete DNS record command
    delete_parser = subparsers.add_parser("delete", help="Delete a DNS record")
    delete_parser.add_argument("--type", required=True, help="Record type")
    delete_parser.add_argument("--name", required=True, help="Record name")
    
    # Setup quantum subdomain command
    quantum_parser = subparsers.add_parser("setup-quantum", help="Setup quantum subdomain")
    quantum_parser.add_argument("--ip", required=True, help="Server IP address")
    
    # Setup API subdomain command
    api_parser = subparsers.add_parser("setup-api", help="Setup API subdomain")
    api_parser.add_argument("--ip", required=True, help="Server IP address")
    
    # Create CNAME record command
    cname_parser = subparsers.add_parser("create-cname", help="Create a CNAME record")
    cname_parser.add_argument("--subdomain", required=True, help="Subdomain name")
    cname_parser.add_argument("--target", required=True, help="Target domain")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check for required credentials
    api_key = args.key or os.environ.get("GODADDY_API_KEY")
    api_secret = args.secret or os.environ.get("GODADDY_API_SECRET")
    
    if not api_key or not api_secret:
        logger.error("GoDaddy API credentials not provided. Use --key and --secret flags or set GODADDY_API_KEY and GODADDY_API_SECRET environment variables.")
        return 1
    
    # Create GoDaddy manager
    manager = GoDaddyManager(args.domain, api_key, api_secret)
    
    # Execute command
    if args.command == "info":
        info = manager.get_domain_info()
        if info:
            print(json.dumps(info, indent=2))
            return 0
        else:
            return 1
    
    elif args.command == "list":
        records = manager.get_dns_records(args.type, args.name)
        if records:
            print(json.dumps(records, indent=2))
            return 0
        else:
            print("No DNS records found")
            return 1
    
    elif args.command == "update":
        success = manager.update_dns_record(args.type, args.name, args.value, args.ttl)
        return 0 if success else 1
    
    elif args.command == "delete":
        success = manager.delete_dns_record(args.type, args.name)
        return 0 if success else 1
    
    elif args.command == "setup-quantum":
        success = manager.setup_quantum_subdomain(args.ip)
        return 0 if success else 1
    
    elif args.command == "setup-api":
        success = manager.setup_api_subdomain(args.ip)
        return 0 if success else 1
    
    elif args.command == "create-cname":
        success = manager.create_cname_record(args.subdomain, args.target)
        return 0 if success else 1
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOL

chmod +x "$GODADDY_SCRIPT"
echo -e "${GREEN}✓ GoDaddy manager script created at $GODADDY_SCRIPT${NC}\n"

# Create environment variables file for credentials
echo -e "${BOLD}Creating environment file for GoDaddy credentials...${NC}"
ENV_FILE="$INSTALL_DIR/.env"

# Check if .env file exists and append to it
if [ -f "$ENV_FILE" ]; then
    # Remove any existing GoDaddy settings
    sed -i '/GODADDY_API_KEY/d' "$ENV_FILE" 
    sed -i '/GODADDY_API_SECRET/d' "$ENV_FILE"
    sed -i '/GODADDY_DOMAIN/d' "$ENV_FILE"
    
    # Add new settings
    echo "" >> "$ENV_FILE"
    echo "# GoDaddy API settings" >> "$ENV_FILE"
    echo "GODADDY_API_KEY=$API_KEY" >> "$ENV_FILE"
    echo "GODADDY_API_SECRET=$API_SECRET" >> "$ENV_FILE"
    echo "GODADDY_DOMAIN=$DOMAIN" >> "$ENV_FILE"
else
    # Create new .env file
    cat > "$ENV_FILE" << EOL
# GoDaddy API settings
GODADDY_API_KEY=$API_KEY
GODADDY_API_SECRET=$API_SECRET
GODADDY_DOMAIN=$DOMAIN
EOL
fi

echo -e "${GREEN}✓ GoDaddy credentials saved to $ENV_FILE${NC}\n"

# Get server IP address
echo -e "${BOLD}Setting up DNS records for your domain...${NC}"
read -p "Enter your server's public IP address: " SERVER_IP

# Set up quantum and API subdomains
echo -e "\n${BOLD}Setting up quantum subdomain...${NC}"
python3 "$GODADDY_SCRIPT" --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" setup-quantum --ip "$SERVER_IP"

echo -e "\n${BOLD}Setting up API subdomain...${NC}"
python3 "$GODADDY_SCRIPT" --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" setup-api --ip "$SERVER_IP"

# Create convenient command aliases
echo -e "\n${BOLD}Creating command aliases...${NC}"
ALIASES_FILE="$INSTALL_DIR/godaddy_aliases.sh"

cat > "$ALIASES_FILE" << EOL
# Aliases for GoDaddy domain management
alias godaddy-info='python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" info'
alias godaddy-list='python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" list'
alias godaddy-update='python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" update'
EOL

echo -e "${GREEN}✓ Command aliases created at $ALIASES_FILE${NC}"
echo -e "${YELLOW}To use them, run: source $ALIASES_FILE${NC}\n"

# Create setup instructions
echo -e "${BOLD}Creating detailed domain setup instructions...${NC}"
INSTRUCTIONS_FILE="$INSTALL_DIR/domain_setup_instructions.md"

cat > "$INSTRUCTIONS_FILE" << EOL
# Domain Setup Instructions for Quantum Consciousness System

## Domain Configuration

Your domain **$DOMAIN** has been configured with the following:

- **quantum.$DOMAIN** points to $SERVER_IP
- **api.$DOMAIN** points to $SERVER_IP

## Accessing Your System

- Web Interface: http://quantum.$DOMAIN:8080
- API Endpoint: http://api.$DOMAIN:8000

## Managing Your Domain

Use the included \`godaddy_manager.py\` script to manage your domain:

\`\`\`bash
# Get domain information
python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" info

# List DNS records
python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" list

# Add or update a DNS record
python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" update --type A --name subdomain --value 192.168.1.1

# Delete a DNS record
python3 $GODADDY_SCRIPT --key "$API_KEY" --secret "$API_SECRET" --domain "$DOMAIN" delete --type A --name subdomain
\`\`\`

## Setting Up SSL (HTTPS)

For production use, we recommend setting up SSL certificates:

1. Install certbot: \`sudo apt-get install certbot\`
2. Get SSL certificates: \`sudo certbot certonly --standalone -d quantum.$DOMAIN -d api.$DOMAIN\`
3. Configure your webserver to use the certificates

## Next Steps

1. Ensure your firewall allows traffic on ports 8080 (web interface) and 8000 (API)
2. Update your system configuration to use your domain names
3. Set up SSL certificates for secure access
EOL

echo -e "${GREEN}✓ Setup instructions created at $INSTRUCTIONS_FILE${NC}\n"

echo -e "${BOLD}${GREEN}GoDaddy Domain Setup Complete!${NC}\n"
echo -e "${YELLOW}Note: DNS changes may take up to 24