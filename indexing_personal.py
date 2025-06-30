#!/usr/bin/env python3
"""
Google Indexing API using your personal Google account
No service account needed - uses your own Google account directly
"""

import json
import sys
import subprocess
import os
from urllib.parse import quote

def login_with_personal_account():
    """Login with personal Google account for Indexing API access"""
    print("This will open your browser to authenticate with your personal Google account...")
    print("Make sure this account has access to your site in Google Search Console.\n")
    
    # Use gcloud to authenticate with additional scopes
    result = subprocess.run([
        'gcloud', 'auth', 'login',
        '--enable-gdrive-access',
        '--add-quota-project-to-adc',
        '--force'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Successfully authenticated with your Google account")
        return True
    else:
        print(f"✗ Authentication failed: {result.stderr}")
        return False

def get_personal_access_token():
    """Get access token from your personal gcloud login"""
    # First, check if user is logged in
    result = subprocess.run([
        'gcloud', 'auth', 'list',
        '--filter=status:ACTIVE',
        '--format=value(account)'
    ], capture_output=True, text=True)
    
    active_account = result.stdout.strip()
    if not active_account:
        print("No active Google account found. Please login first.")
        if login_with_personal_account():
            return get_personal_access_token()
        else:
            sys.exit(1)
    
    print(f"Using account: {active_account}")
    
    # Get access token
    result = subprocess.run([
        'gcloud', 'auth', 'print-access-token'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print(f"Error getting access token: {result.stderr}")
        sys.exit(1)

def check_search_console_access(access_token):
    """Check if we have access to Search Console"""
    result = subprocess.run([
        'curl', '-s',
        'https://www.googleapis.com/webmasters/v3/sites',
        '-H', f'Authorization: Bearer {access_token}'
    ], capture_output=True, text=True)
    
    try:
        response = json.loads(result.stdout)
        if 'error' in response:
            return False, response['error'].get('message', 'Unknown error')
        else:
            sites = response.get('siteEntry', [])
            return True, sites
    except:
        return False, "Failed to check Search Console access"

def submit_url_personal(url, action="URL_UPDATED"):
    """Submit URL using personal account"""
    access_token = get_personal_access_token()
    
    # First check Search Console access
    has_access, info = check_search_console_access(access_token)
    if has_access:
        print(f"✓ Search Console access confirmed")
        if isinstance(info, list) and info:
            print("Your verified sites:")
            for site in info:
                print(f"  - {site.get('siteUrl', 'Unknown')}")
    else:
        print(f"⚠️  Warning: Cannot verify Search Console access: {info}")
        print("Make sure you have verified your site in Search Console with this account.")
    
    # Try to submit anyway
    data = json.dumps({
        "url": url,
        "type": action
    })
    
    project_id = subprocess.run([
        'gcloud', 'config', 'get-value', 'project'
    ], capture_output=True, text=True).stdout.strip()
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://indexing.googleapis.com/v3/urlNotifications:publish',
        '-H', f'Authorization: Bearer {access_token}',
        '-H', 'Content-Type: application/json',
        '-H', f'x-goog-user-project: {project_id}',
        '-d', data
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

def get_url_status_personal(url):
    """Get URL status using personal account"""
    access_token = get_personal_access_token()
    
    project_id = subprocess.run([
        'gcloud', 'config', 'get-value', 'project'
    ], capture_output=True, text=True).stdout.strip()
    
    result = subprocess.run([
        'curl', '-s', '-X', 'GET',
        f'https://indexing.googleapis.com/v3/urlNotifications/metadata?url={quote(url)}',
        '-H', f'Authorization: Bearer {access_token}',
        '-H', f'x-goog-user-project: {project_id}'
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

def main():
    if len(sys.argv) < 2:
        print("Google Indexing API - Personal Account")
        print("=====================================")
        print("\nUsage:")
        print("  python indexing_personal.py login      # Login with your Google account")
        print("  python indexing_personal.py submit <url>")
        print("  python indexing_personal.py delete <url>")
        print("  python indexing_personal.py status <url>")
        print("  python indexing_personal.py sites      # List your Search Console sites")
        print("\nRequirements:")
        print("  1. Your Google account must have verified the site in Search Console")
        print("  2. The Indexing API must be enabled in your Google Cloud project")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "login":
        if login_with_personal_account():
            print("\n✓ Login successful!")
            print("You can now use the submit/delete/status commands.")
    
    elif command == "sites":
        access_token = get_personal_access_token()
        has_access, sites = check_search_console_access(access_token)
        if has_access and isinstance(sites, list):
            print("\nYour verified sites in Search Console:")
            for site in sites:
                print(f"  - {site.get('siteUrl', 'Unknown')}")
                print(f"    Permission: {site.get('permissionLevel', 'Unknown')}")
        else:
            print(f"Error accessing Search Console: {sites}")
    
    elif command in ["submit", "delete", "status"]:
        if len(sys.argv) < 3:
            print(f"Error: {command} requires a URL")
            sys.exit(1)
        
        url = sys.argv[2]
        
        if command == "status":
            result = get_url_status_personal(url)
        else:
            action = "URL_DELETED" if command == "delete" else "URL_UPDATED"
            result = submit_url_personal(url, action)
        
        print("\nResult:")
        print(json.dumps(result, indent=2))
        
        if 'error' in result:
            print("\n⚠️  Error occurred!")
            if result['error'].get('code') == 403:
                print("Make sure:")
                print("1. You've verified this site in Google Search Console")
                print("2. You're using the same Google account that verified the site")
                print("3. The Indexing API is enabled in your project")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()