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
from typing import Dict, List, Any

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
