#!/usr/bin/env python3
"""Generate sitemaps for all domains"""

import os
from datetime import datetime

domains = [
    "mysimplestack.com",
    "simple.company", 
    "thesimple.co",
    "textmaya.ai",
    "goodseeds.club"
]

# Common pages most sites have
common_pages = [
    "",  # homepage
    "about",
    "contact",
    "privacy",
    "terms"
]

sitemap_template = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>'''

url_template = '''  <url>
    <loc>{url}</loc>
    <lastmod>{date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>'''

def generate_sitemap(domain):
    """Generate sitemap for a domain"""
    urls = []
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Add homepage with highest priority
    urls.append(url_template.format(
        url=f"https://{domain}/",
        date=date,
        priority="1.0"
    ))
    
    # Add www version
    urls.append(url_template.format(
        url=f"https://www.{domain}/",
        date=date,
        priority="1.0"
    ))
    
    # Add common pages
    for page in common_pages[1:]:  # Skip empty string (homepage)
        urls.append(url_template.format(
            url=f"https://{domain}/{page}",
            date=date,
            priority="0.8"
        ))
    
    sitemap_content = sitemap_template.format(urls="\n".join(urls))
    
    # Save sitemap
    filename = f"sitemap_{domain.replace('.', '_')}.xml"
    with open(filename, 'w') as f:
        f.write(sitemap_content)
    
    print(f"✅ Generated {filename}")
    return filename

def generate_robots(domain):
    """Generate robots.txt for a domain"""
    robots_content = f"""# Robots.txt for {domain}
User-agent: *
Allow: /

# Sitemap
Sitemap: https://{domain}/sitemap.xml
Sitemap: https://www.{domain}/sitemap.xml

# Crawl delay for politeness
Crawl-delay: 1

# Block admin/private areas if they exist
Disallow: /admin/
Disallow: /private/
Disallow: /.git/
Disallow: /api/private/
"""
    
    filename = f"robots_{domain.replace('.', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(robots_content)
    
    print(f"✅ Generated {filename}")
    return filename

print("Generating Sitemaps and Robots.txt Files")
print("========================================\n")

for domain in domains:
    print(f"\nProcessing {domain}:")
    print("-" * 30)
    
    # Skip castit.ai since it's not accessible
    if domain == "castit.ai":
        print("⚠️  Skipping castit.ai (site not accessible)")
        continue
    
    sitemap_file = generate_sitemap(domain)
    robots_file = generate_robots(domain)

print("\n\n📋 Next Steps:")
print("=============")
print("\n1. Upload these files to your web servers:")
print("   - Upload sitemap_*.xml as /sitemap.xml on each domain")
print("   - Upload robots_*.txt as /robots.txt on each domain")

print("\n2. Submit sitemaps in Google Search Console:")
for domain in domains:
    if domain != "castit.ai":
        print(f"   - https://search.google.com/search-console?resource_id=sc-domain:{domain}")

print("\n3. Test your robots.txt files:")
for domain in domains:
    if domain != "castit.ai":
        print(f"   - https://{domain}/robots.txt")

print("\n4. Validate sitemaps:")
print("   - https://www.xml-sitemaps.com/validate-xml-sitemap.html")