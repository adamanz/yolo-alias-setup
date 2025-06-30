#!/usr/bin/env python3
"""
Google Search Console Indexing API Tool
Uses Application Default Credentials to submit URLs for indexing
"""

import json
import sys
from typing import List, Dict
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth
import requests

def get_access_token() -> str:
    """Get access token using Application Default Credentials"""
    try:
        # Use Application Default Credentials
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        
        # Refresh the credentials if needed
        request = Request()
        credentials.refresh(request)
        
        return credentials.token
    except Exception as e:
        print(f"Error getting access token: {e}")
        print("Make sure you've run: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/indexing")
        sys.exit(1)

def submit_url(url: str, access_token: str, action: str = "URL_UPDATED") -> Dict:
    """
    Submit a URL to Google's Indexing API
    
    Args:
        url: The URL to submit
        access_token: Google Cloud access token
        action: Either 'URL_UPDATED' or 'URL_DELETED'
    
    Returns:
        API response as dict
    """
    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "url": url,
        "type": action
    }
    
    response = requests.post(endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": True,
            "status_code": response.status_code,
            "message": response.text
        }

def get_url_status(url: str, access_token: str) -> Dict:
    """
    Get indexing status for a URL
    
    Args:
        url: The URL to check
        access_token: Google Cloud access token
    
    Returns:
        API response as dict
    """
    endpoint = "https://indexing.googleapis.com/v3/urlNotifications/metadata"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    params = {
        "url": url
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": True,
            "status_code": response.status_code,
            "message": response.text
        }

def batch_submit_urls(urls: List[str], access_token: str, action: str = "URL_UPDATED") -> List[Dict]:
    """
    Submit multiple URLs for indexing
    
    Args:
        urls: List of URLs to submit
        access_token: Google Cloud access token
        action: Either 'URL_UPDATED' or 'URL_DELETED'
    
    Returns:
        List of API responses
    """
    results = []
    for url in urls:
        print(f"Submitting: {url}")
        result = submit_url(url, access_token, action)
        results.append({
            "url": url,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        if "error" in result:
            print(f"  Error: {result['message']}")
        else:
            print(f"  Success: {result}")
    
    return results

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python indexing_tool.py submit <url> [url2 url3 ...]")
        print("  python indexing_tool.py delete <url> [url2 url3 ...]")
        print("  python indexing_tool.py status <url>")
        print("  python indexing_tool.py batch <file_with_urls.txt>")
        sys.exit(1)
    
    command = sys.argv[1]
    access_token = get_access_token()
    
    if command == "submit":
        if len(sys.argv) < 3:
            print("Error: Please provide at least one URL to submit")
            sys.exit(1)
        
        urls = sys.argv[2:]
        results = batch_submit_urls(urls, access_token, "URL_UPDATED")
        
        # Save results
        with open("indexing_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to indexing_results.json")
        
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Please provide at least one URL to delete")
            sys.exit(1)
        
        urls = sys.argv[2:]
        results = batch_submit_urls(urls, access_token, "URL_DELETED")
        
        # Save results
        with open("deletion_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to deletion_results.json")
        
    elif command == "status":
        if len(sys.argv) < 3:
            print("Error: Please provide a URL to check")
            sys.exit(1)
        
        url = sys.argv[2]
        result = get_url_status(url, access_token)
        
        if "error" in result:
            print(f"Error: {result['message']}")
        else:
            print(json.dumps(result, indent=2))
            
    elif command == "batch":
        if len(sys.argv) < 3:
            print("Error: Please provide a file path containing URLs")
            sys.exit(1)
        
        file_path = sys.argv[2]
        try:
            with open(file_path, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            results = batch_submit_urls(urls, access_token, "URL_UPDATED")
            
            # Save results
            with open("batch_indexing_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"\nProcessed {len(urls)} URLs")
            print(f"Results saved to batch_indexing_results.json")
            
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            sys.exit(1)
    
    else:
        print(f"Error: Unknown command '{command}'")
        print("Valid commands: submit, delete, status, batch")
        sys.exit(1)

if __name__ == "__main__":
    main()