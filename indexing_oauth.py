#!/usr/bin/env python3
"""
Google Indexing API with OAuth2 Authentication
Uses your personal Google account (no service account needed)
"""

import json
import sys
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import subprocess
import os
import socket

# OAuth2 Configuration - Using Google's public OAuth client for installed apps
CLIENT_ID = "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"
CLIENT_SECRET = "d-FL95Q19q7MQmFpd7hHD0Ty"  # This is public for installed apps
REDIRECT_URI = "http://localhost:8085"  # Using same port as gcloud
SCOPES = ["https://www.googleapis.com/auth/indexing", "https://www.googleapis.com/auth/webmasters"]

# Store tokens
TOKEN_FILE = os.path.expanduser("~/.indexing_tokens.json")

class AuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback"""
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>Authorization Successful</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #4CAF50;">✓ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Authorization failed</h1></body></html>')
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def get_auth_code():
    """Open browser for OAuth2 authentication"""
    # Find an available port
    port = 8085
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port < 8095:
        try:
            sock.bind(('localhost', port))
            sock.close()
            break
        except:
            port += 1
    
    redirect_uri = f"http://localhost:{port}"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote(' '.join(SCOPES))}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    # Start local server
    server = HTTPServer(('localhost', port), AuthHandler)
    server.auth_code = None
    
    # Open browser
    print(f"Opening browser for authentication...")
    print(f"If browser doesn't open, visit this URL:")
    print(f"\n{auth_url}\n")
    webbrowser.open(auth_url)
    
    # Wait for callback
    print(f"Waiting for authorization (listening on port {port})...")
    server.handle_request()
    
    if server.auth_code:
        print("✓ Authorization code received!")
        return server.auth_code, redirect_uri
    else:
        raise Exception("Authentication failed or timeout")

def exchange_code_for_tokens(code, redirect_uri):
    """Exchange authorization code for tokens"""
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://oauth2.googleapis.com/token',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '-d', '&'.join([f"{k}={v}" for k, v in data.items()])
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

def refresh_access_token(refresh_token):
    """Get new access token using refresh token"""
    data = {
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://oauth2.googleapis.com/token',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '-d', '&'.join([f"{k}={v}" for k, v in data.items()])
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

def get_access_token():
    """Get valid access token, refreshing if needed"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
        
        # Try to refresh
        new_tokens = refresh_access_token(tokens['refresh_token'])
        if 'access_token' in new_tokens:
            tokens.update(new_tokens)
            with open(TOKEN_FILE, 'w') as f:
                json.dump(tokens, f)
            return tokens['access_token']
    
    # Need new authentication
    print("Need to authenticate with Google...")
    code, redirect_uri = get_auth_code()
    tokens = exchange_code_for_tokens(code, redirect_uri)
    
    if 'error' in tokens:
        print(f"Error exchanging code: {tokens}")
        raise Exception("Failed to get access token")
    
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)
    
    return tokens['access_token']

def submit_url(url, action="URL_UPDATED"):
    """Submit URL to Indexing API"""
    access_token = get_access_token()
    
    data = json.dumps({
        "url": url,
        "type": action
    })
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://indexing.googleapis.com/v3/urlNotifications:publish',
        '-H', f'Authorization: Bearer {access_token}',
        '-H', 'Content-Type: application/json',
        '-d', data
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

def main():
    if len(sys.argv) < 2:
        print("Google Indexing API - OAuth Authentication")
        print("=========================================")
        print("\nUsage:")
        print("  python indexing_oauth.py auth       # Authenticate with Google")
        print("  python indexing_oauth.py submit <url>")
        print("  python indexing_oauth.py delete <url>")
        print("  python indexing_oauth.py status <url>")
        print("\nNote: You must have verified your site in Google Search Console")
        print("      with the Google account you use to authenticate.")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "auth":
        # Force re-authentication
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        try:
            get_access_token()
            print("\n✓ Authentication successful! You can now use submit/delete commands.")
        except Exception as e:
            print(f"\n✗ Authentication failed: {e}")
            sys.exit(1)
    
    elif command in ["submit", "delete", "status"]:
        if len(sys.argv) < 3:
            print(f"Error: {command} command requires a URL")
            sys.exit(1)
        
        url = sys.argv[2]
        
        try:
            if command == "submit":
                result = submit_url(url, "URL_UPDATED")
            elif command == "delete":
                result = submit_url(url, "URL_DELETED")
            else:  # status
                # Add status check function
                access_token = get_access_token()
                result = subprocess.run([
                    'curl', '-s', '-X', 'GET',
                    f'https://indexing.googleapis.com/v3/urlNotifications/metadata?url={urllib.parse.quote(url)}',
                    '-H', f'Authorization: Bearer {access_token}'
                ], capture_output=True, text=True)
                result = json.loads(result.stdout)
            
            print("\nResult:")
            print(json.dumps(result, indent=2))
            
            if 'error' in result and result['error'].get('code') == 403:
                print("\n⚠️  Access denied. Make sure you've verified this site in")
                print("   Google Search Console with the account you authenticated with.")
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python indexing_oauth.py' for usage information")
        sys.exit(1)

if __name__ == "__main__":
    main()