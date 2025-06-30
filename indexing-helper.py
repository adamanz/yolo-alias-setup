#!/usr/bin/env python3
"""
Google Search Console Indexing Helper
Helps you manage indexing for your sites
"""

import json
import sys
import webbrowser
import os
from datetime import datetime

def show_menu():
    """Show main menu"""
    print("\nGoogle Search Console Indexing Helper")
    print("=====================================\n")
    print("1. Open Google Search Console")
    print("2. Check indexing for a specific URL") 
    print("3. Submit URLs for indexing (batch)")
    print("4. Create sitemap.xml")
    print("5. Check robots.txt")
    print("6. Generate indexing report")
    print("0. Exit\n")

def open_search_console():
    """Open Search Console in browser"""
    print("Opening Google Search Console...")
    webbrowser.open("https://search.google.com/search-console")
    print("\nIn Search Console, you can:")
    print("- See all your verified properties")
    print("- Check Coverage report for indexing issues")
    print("- Submit sitemaps")
    print("- Use URL Inspection tool")

def check_url_indexing():
    """Guide user to check URL indexing"""
    url = input("\nEnter URL to check: ").strip()
    
    print(f"\nTo check indexing for: {url}")
    print("\n1. Opening URL Inspection tool...")
    inspection_url = f"https://search.google.com/search-console/inspect?resource_id={url}"
    webbrowser.open(inspection_url)
    
    print("\n2. You can also search Google directly:")
    search_url = f"https://www.google.com/search?q=site:{url}"
    print(f"   {search_url}")
    
    print("\n3. Common indexing issues to check:")
    print("   - Page not found (404)")
    print("   - Blocked by robots.txt")
    print("   - Noindex tag present")
    print("   - Canonical pointing elsewhere")
    print("   - Server errors (5xx)")

def batch_submit_urls():
    """Create a batch file for URL submission"""
    print("\nBatch URL Submission")
    print("====================")
    
    urls = []
    print("Enter URLs to submit (one per line, empty line to finish):")
    
    while True:
        url = input().strip()
        if not url:
            break
        urls.append(url)
    
    if urls:
        # Save URLs to file
        filename = f"urls_to_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            for url in urls:
                f.write(url + '\n')
        
        print(f"\n✓ Saved {len(urls)} URLs to {filename}")
        
        # Create submission script
        script_name = "submit_urls.sh"
        with open(script_name, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Submit URLs to Google Indexing API\n\n")
            f.write("echo 'Submitting URLs for indexing...'\n\n")
            
            for url in urls:
                f.write(f"echo 'Submitting: {url}'\n")
                f.write(f"./gindex-simple submit '{url}'\n")
                f.write("echo ''\n")
                f.write("sleep 1  # Rate limiting\n\n")
        
        os.chmod(script_name, 0o755)
        print(f"✓ Created submission script: {script_name}")
        print(f"\nTo submit all URLs, run: ./{script_name}")

def create_sitemap():
    """Help create a sitemap"""
    print("\nSitemap Generator")
    print("=================")
    
    domain = input("Enter your domain (e.g., https://example.com): ").strip()
    
    urls = []
    print("\nEnter page paths (e.g., /about, /contact):")
    print("Empty line to finish")
    
    while True:
        path = input().strip()
        if not path:
            break
        if not path.startswith('/'):
            path = '/' + path
        urls.append(domain + path)
    
    if urls:
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            sitemap += '  <url>\n'
            sitemap += f'    <loc>{url}</loc>\n'
            sitemap += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
            sitemap += '    <changefreq>weekly</changefreq>\n'
            sitemap += '    <priority>0.8</priority>\n'
            sitemap += '  </url>\n'
        
        sitemap += '</urlset>'
        
        with open('sitemap.xml', 'w') as f:
            f.write(sitemap)
        
        print(f"\n✓ Created sitemap.xml with {len(urls)} URLs")
        print("\nNext steps:")
        print("1. Upload sitemap.xml to your website root")
        print("2. Submit it in Search Console")
        print(f"3. Add to robots.txt: Sitemap: {domain}/sitemap.xml")

def check_robots():
    """Check robots.txt"""
    domain = input("\nEnter domain to check (e.g., https://example.com): ").strip()
    
    robots_url = f"{domain}/robots.txt"
    print(f"\nOpening robots.txt checker for: {robots_url}")
    
    # Open Google's robots.txt tester
    tester_url = f"https://www.google.com/webmasters/tools/robots-testing-tool?hl=en&siteUrl={domain}"
    webbrowser.open(tester_url)
    
    print("\nCommon robots.txt issues:")
    print("- Disallow: / (blocks entire site)")
    print("- Missing sitemap declaration")
    print("- Blocking important resources (CSS/JS)")
    print("- Wrong user-agent rules")

def generate_report():
    """Generate indexing report"""
    print("\nIndexing Report Generator")
    print("=========================")
    
    sites = []
    print("Enter your sites (empty line to finish):")
    
    while True:
        site = input().strip()
        if not site:
            break
        sites.append(site)
    
    if sites:
        report = f"Indexing Status Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 50 + "\n\n"
        
        for site in sites:
            report += f"Site: {site}\n"
            report += "-" * 30 + "\n"
            report += "Check the following:\n"
            report += "[ ] Verified in Search Console\n"
            report += "[ ] Sitemap submitted\n"
            report += "[ ] No robots.txt blocking\n"
            report += "[ ] Mobile-friendly\n"
            report += "[ ] HTTPS enabled\n"
            report += "[ ] Core Web Vitals passing\n"
            report += "[ ] No manual penalties\n"
            report += "[ ] Indexed pages count: ___\n"
            report += f"\nSearch Console: https://search.google.com/search-console?resource_id={site}\n"
            report += f"PageSpeed: https://pagespeed.web.dev/report?url={site}\n"
            report += f"Mobile Test: https://search.google.com/test/mobile-friendly?url={site}\n"
            report += "\n\n"
        
        filename = f"indexing_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"\n✓ Report saved to: {filename}")

def main():
    while True:
        show_menu()
        choice = input("Select option: ").strip()
        
        if choice == '0':
            print("\nGoodbye!")
            break
        elif choice == '1':
            open_search_console()
        elif choice == '2':
            check_url_indexing()
        elif choice == '3':
            batch_submit_urls()
        elif choice == '4':
            create_sitemap()
        elif choice == '5':
            check_robots()
        elif choice == '6':
            generate_report()
        else:
            print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()