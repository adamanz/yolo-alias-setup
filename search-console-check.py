#!/usr/bin/env python3
"""
Check all Google Search Console sites using the newer API
"""

import json
import subprocess
import sys
import os
from urllib.parse import quote
from datetime import datetime, timedelta

def get_access_token():
    """Get access token from ADC"""
    # Read ADC file
    adc_path = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    
    try:
        with open(adc_path, 'r') as f:
            creds = json.load(f)
        
        # Get fresh token
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'https://oauth2.googleapis.com/token',
            '-d', f"client_id={creds['client_id']}",
            '-d', f"client_secret={creds['client_secret']}",  
            '-d', f"refresh_token={creds['refresh_token']}",
            '-d', 'grant_type=refresh_token'
        ], capture_output=True, text=True)
        
        token_data = json.loads(result.stdout)
        
        if 'access_token' in token_data:
            return token_data['access_token']
        else:
            print(f"Error in token response: {token_data}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error getting token: {e}")
        sys.exit(1)

def make_api_call(url, token, method='GET', data=None):
    """Make API call using curl"""
    cmd = ['curl', '-s', '-X', method, url]
    cmd.extend(['-H', f'Authorization: Bearer {token}'])
    cmd.extend(['-H', 'x-goog-user-project: titanium-vision-455301-c4'])
    
    if data:
        cmd.extend(['-H', 'Content-Type: application/json'])
        cmd.extend(['-d', json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stdout}

def list_sites(token):
    """List all verified sites"""
    print("Fetching verified sites from Google Search Console...")
    
    # Try Search Console API v1
    url = "https://searchconsole.googleapis.com/v1/sites"
    response = make_api_call(url, token)
    
    if 'error' in response:
        # Fallback to Webmasters API v3
        print("Trying Webmasters API...")
        url = "https://www.googleapis.com/webmasters/v3/sites"
        response = make_api_call(url, token)
    
    return response

def check_indexing_coverage(token, site_url):
    """Check indexing coverage for a site"""
    encoded_url = quote(site_url, safe='')
    
    # Try to get index coverage data
    url = f"https://searchconsole.googleapis.com/v1/sites/{encoded_url}/indexCoverage"
    response = make_api_call(url, token)
    
    return response

def check_url_inspection(token, site_url, page_url):
    """Inspect a specific URL"""
    encoded_site = quote(site_url, safe='')
    
    url = f"https://searchconsole.googleapis.com/v1/sites/{encoded_site}/urlInspection"
    data = {
        "inspectionUrl": page_url,
        "siteUrl": site_url
    }
    
    response = make_api_call(url, token, 'POST', data)
    return response

def check_search_analytics(token, site_url):
    """Get search analytics for the site"""
    encoded_url = quote(site_url, safe='')
    
    # Get data for last 7 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://www.googleapis.com/webmasters/v3/sites/{encoded_url}/searchAnalytics/query"
    data = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query", "page"],
        "rowLimit": 10,
        "startRow": 0
    }
    
    response = make_api_call(url, token, 'POST', data)
    return response

def main():
    print("Google Search Console Site Checker")
    print("==================================\n")
    
    # Get access token
    token = get_access_token()
    print("✓ Authentication successful\n")
    
    # List all sites
    sites_response = list_sites(token)
    
    if 'siteEntry' in sites_response:
        sites = sites_response['siteEntry']
        print(f"Found {len(sites)} verified sites:\n")
        
        for site in sites:
            site_url = site['siteUrl']
            permission = site.get('permissionLevel', 'unknown')
            
            print(f"Site: {site_url}")
            print(f"Permission: {permission}")
            print("-" * 50)
            
            # Check search analytics
            print("Checking search performance...")
            analytics = check_search_analytics(token, site_url)
            
            if 'rows' in analytics and analytics['rows']:
                total_clicks = sum(row.get('clicks', 0) for row in analytics['rows'])
                total_impressions = sum(row.get('impressions', 0) for row in analytics['rows'])
                print(f"Last 7 days: {total_clicks} clicks, {total_impressions} impressions")
                
                # Show top queries
                queries = {}
                for row in analytics['rows']:
                    if 'query' in row['keys']:
                        query = row['keys'][0]
                        queries[query] = queries.get(query, 0) + row.get('clicks', 0)
                
                if queries:
                    print("\nTop search queries:")
                    for query, clicks in sorted(queries.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"  - {query}: {clicks} clicks")
            else:
                print("No search data available")
            
            # Try to check indexing coverage
            print("\nChecking indexing status...")
            coverage = check_indexing_coverage(token, site_url)
            
            if 'error' not in coverage:
                print(json.dumps(coverage, indent=2))
            else:
                print("Indexing coverage data not available")
            
            print("\n" + "=" * 50 + "\n")
            
            # Save site data
            filename = f"site_data_{site_url.replace('://', '_').replace('/', '_')}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'site': site,
                    'analytics': analytics,
                    'coverage': coverage,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
    
    elif 'sites' in sites_response:
        # New API format
        sites = sites_response['sites']
        print(f"Found {len(sites)} sites")
        for site in sites:
            print(f"- {site}")
    else:
        print("No sites found or unable to access Search Console")
        print(f"Response: {json.dumps(sites_response, indent=2)}")
        
        print("\nMake sure you have:")
        print("1. Verified sites in Google Search Console")
        print("2. Used the same Google account for authentication")
        print("3. Proper API permissions")

if __name__ == "__main__":
    main()