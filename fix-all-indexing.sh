#!/bin/bash
# Fix indexing for all your sites

echo "Fixing Indexing for All Your Sites"
echo "=================================="
echo ""

# Your verified sites
SITES=(
    "https://mysimplestack.com"
    "https://www.mysimplestack.com"
    "https://simple.company"
    "https://www.simple.company"
    "https://thesimple.co"
    "https://www.thesimple.co"
    "https://castit.ai"
    "https://www.castit.ai"
    "https://textmaya.ai"
    "https://www.textmaya.ai"
    "https://goodseeds.club"
    "https://www.goodseeds.club"
)

# Function to submit URL with error handling
submit_url() {
    local url=$1
    echo "Submitting: $url"
    
    # Use the indexing tool
    response=$(./gindex-simple submit "$url" 2>&1)
    
    if echo "$response" | grep -q "error"; then
        echo "  ❌ Error submitting"
        echo "$response" | grep -i error
    else
        echo "  ✅ Submitted successfully"
    fi
    echo ""
}

# Function to check robots.txt
check_robots() {
    local domain=$1
    echo "Checking robots.txt for $domain..."
    curl -s "$domain/robots.txt" | head -10
    echo ""
}

# Function to check if site is live
check_site() {
    local url=$1
    echo "Checking if $url is accessible..."
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    echo "  HTTP Status: $status_code"
    
    if [ "$status_code" = "200" ]; then
        echo "  ✅ Site is accessible"
    else
        echo "  ❌ Site may have issues (status: $status_code)"
    fi
    echo ""
}

# Main process
echo "Step 1: Checking site accessibility"
echo "-----------------------------------"
for site in "${SITES[@]}"; do
    check_site "$site"
    sleep 0.5
done

echo ""
echo "Step 2: Checking robots.txt files"
echo "---------------------------------"
for site in "${SITES[@]}"; do
    # Only check base domains
    if [[ ! "$site" =~ www\. ]]; then
        check_robots "$site"
    fi
done

echo ""
echo "Step 3: Submitting all URLs for indexing"
echo "----------------------------------------"
echo "This will submit each URL to Google's Indexing API..."
echo ""

read -p "Continue with submission? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for site in "${SITES[@]}"; do
        submit_url "$site"
        sleep 1  # Rate limiting
    done
    
    echo ""
    echo "✅ All submissions complete!"
    echo ""
    echo "Next steps:"
    echo "1. Check Google Search Console in 24-48 hours"
    echo "2. Submit sitemaps for each domain"
    echo "3. Fix any robots.txt issues"
    echo "4. Ensure all sites have proper SSL certificates"
    echo ""
    echo "View your Search Console at:"
    echo "https://search.google.com/search-console"
else
    echo "Submission cancelled."
fi