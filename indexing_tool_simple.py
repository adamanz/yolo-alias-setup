#!/usr/bin/env python3
"""
Google Search Console Indexing API Tool - Simple Version
Uses gcloud ADC credentials to submit URLs for indexing
"""

import json
import sys
import subprocess
from typing import List, Dict
from datetime import datetime

def get_adc_token() -> str:
    """Get access token from Application Default Credentials"""
    try:
        # Read the ADC file
        with open('/Users/adamanzuoni/.config/gcloud/application_default_credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Get access token using refresh token
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'https://oauth2.googleapis.com/token',
            '-H', 'Content-Type: application/x-www-form-urlencoded',
            '-d', f"client_id={creds['client_id']}",
            '-d', f"client_secret={creds['client_secret']}",
            '-d', f"refresh_token={creds['refresh_token']}",
            '-d', 'grant_type=refresh_token',
            '-d', 'scope=https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/indexing'
        ], capture_output=True, text=True)
        
        token_data = json.loads(result.stdout)
        if 'access_token' not in token_data:
            print(f"Token response: {token_data}")
            raise Exception("No access token in response")
        return token_data['access_token']
    except Exception as e:
        print(f"Error getting access token: {e}")
        sys.exit(1)

def submit_url(url: str, access_token: str, action: str = "URL_UPDATED") -> Dict:
    """Submit a URL to Google's Indexing API"""
    
    data = json.dumps({
        "url": url,
        "type": action
    })
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://indexing.googleapis.com/v3/urlNotifications:publish',
        '-H', f'Authorization: Bearer {access_token}',
        '-H', 'Content-Type: application/json',
        '-H', 'x-goog-user-project: titanium-vision-455301-c4',
        '-d', data
    ], capture_output=True, text=True)
    
    try:
        return json.loads(result.stdout)
    except:
        return {"error": True, "message": result.stdout}

def get_url_status(url: str, access_token: str) -> Dict:
    """Get indexing status for a URL"""
    
    result = subprocess.run([
        'curl', '-s', '-X', 'GET',
        f'https://indexing.googleapis.com/v3/urlNotifications/metadata?url={url}',
        '-H', f'Authorization: Bearer {access_token}',
        '-H', 'x-goog-user-project: titanium-vision-455301-c4'
    ], capture_output=True, text=True)
    
    try:
        return json.loads(result.stdout)
    except:
        return {"error": True, "message": result.stdout}

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python indexing_tool_simple.py submit <url>")
        print("  python indexing_tool_simple.py delete <url>")
        print("  python indexing_tool_simple.py status <url>")
        print("  python indexing_tool_simple.py test")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        # Test with a dummy URL to check API access
        print("Testing Indexing API access...")
        access_token = get_adc_token()
        print(f"Got access token: {access_token[:20]}...")
        
        result = get_url_status("https://example.com", access_token)
        print("\nAPI Response:")
        print(json.dumps(result, indent=2))
        
        if "error" in result and result.get("error", {}).get("code") == 403:
            print("\n⚠️  Access denied. Make sure to:")
            print("1. Verify your site in Google Search Console")
            print("2. Add the service account as an owner in Search Console")
            print("3. Service account: indexing-api-sa@titanium-vision-455301-c4.iam.gserviceaccount.com")
        return
    
    if len(sys.argv) < 3:
        print(f"Error: {command} command requires a URL")
        sys.exit(1)
    
    url = sys.argv[2]
    access_token = get_adc_token()
    
    if command == "submit":
        print(f"Submitting URL for indexing: {url}")
        result = submit_url(url, access_token, "URL_UPDATED")
        print(json.dumps(result, indent=2))
        
    elif command == "delete":
        print(f"Requesting URL removal: {url}")
        result = submit_url(url, access_token, "URL_DELETED")
        print(json.dumps(result, indent=2))
        
    elif command == "status":
        print(f"Checking indexing status for: {url}")
        result = get_url_status(url, access_token)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()