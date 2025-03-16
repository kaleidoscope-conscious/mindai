#!/usr/bin/env python3
import requests
import json
import os
from typing import List, Dict
import boto3
from dataclasses import dataclass

@dataclass
class GoDaddyConfig:
    api_key: str
    api_secret: str
    domain: str
    base_url: str = "https://api.godaddy.com/v1"

class DomainManager:
    def __init__(self, config: GoDaddyConfig):
        self.config = config
        self.headers = {
            "Authorization": f"sso-key {config.api_key}:{config.api_secret}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # AWS integration
        self.route53 = boto3.client('route53')

    def get_domain_records(self) -> List[Dict]:
        """Get current DNS records"""
        response = self.session.get(
            f"{self.config.base_url}/domains/{self.config.domain}/records"
        )
        response.raise_for_status()
        return response.json()

    def update_nameservers(self, nameservers: List[str]):
        """Update domain nameservers"""
        data = {
            "nameServers": nameservers
        }
        response = self.session.put(
            f"{self.config.base_url}/domains/{self.config.domain}",
            json=data
        )
        response.raise_for_status()
        return response.json()

    def add_dns_record(self, record_type: str, name: str, value: str, ttl: int = 600):
        """Add new DNS record"""
        data = [{
            "type": record_type,
            "name": name,
            "data": value,
            "ttl": ttl
        }]
        response = self.session.patch(
            f"{self.config.base_url}/domains/{self.config.domain}/records",
            json=data
        )
        response.raise_for_status()
        return response.json()

    def setup_aws_routing(self, alb_dns: str):
        """Setup AWS Route53 and update GoDaddy nameservers"""
        # Create Route53 hosted zone
        hosted_zone = self.route53.create_hosted_zone(
            Name=self.config.domain,
            CallerReference=str(hash(self.config.domain + str(os.urandom(8))))
        )
        
        # Get AWS nameservers
        aws_nameservers = hosted_zone['DelegationSet']['NameServers']
        
        # Update GoDaddy nameservers
        self.update_nameservers(aws_nameservers)
        
        # Create A record for ALB
        self.route53.change_resource_record_sets(
            HostedZoneId=hosted_zone['HostedZone']['Id'],
            ChangeBatch={
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': self.config.domain,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': 'Z35SXDOTRQ7X7K',  # ALB hosted zone ID
                            'DNSName': alb_dns,
                            'EvaluateTargetHealth': True
                        }
                    }
                }]
            }
        )

if __name__ == "__main__":
    # Load credentials from environment or AWS Secrets Manager
    secrets = boto3.client('secretsmanager').get_secret_value(
        SecretId='kaleidoscope/godaddy'
    )
    godaddy_creds = json.loads(secrets['SecretString'])
    
    config = GoDaddyConfig(
        api_key=godaddy_creds['api_key'],
        api_secret=godaddy_creds['api_secret'],
        domain="artificialthinker.com"
    )
    
    domain_manager = DomainManager(config)
    
    # Get ALB DNS from AWS
    alb_dns = boto3.client('elbv2').describe_load_balancers(
        Names=['kaleidoscope-alb']
    )['LoadBalancers'][0]['DNSName']
    
    # Setup routing
    domain_manager.setup_aws_routing(alb_dns)

# Store this in AWS Secrets Manager:
secrets_json = {
    "api_key": "YOUR_GODADDY_API_KEY",
    "api_secret": "YOUR_GODADDY_API_SECRET"
}

# Commands to store in AWS Secrets Manager:
aws secretsmanager create-secret \
    --name kaleidoscope/godaddy \
    --secret-string '{"api_key":"YOUR_GODADDY_API_KEY","api_secret":"YOUR_GODADDY_API_SECRET"}'

# Update existing secret:
aws secretsmanager update-secret \
    --secret-id kaleidoscope/godaddy \
    --secret-string '{"api_key":"YOUR_GODADDY_API_KEY","api_secret":"YOUR_GODADDY_API_SECRET"}'