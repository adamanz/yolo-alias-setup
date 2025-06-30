#!/bin/bash
# Check all Google Search Console sites and their indexing status

echo "Google Search Console Site Checker"
echo "=================================="
echo ""

# Get access token from ADC
get_token() {
    local adc_file="$HOME/.config/gcloud/application_default_credentials.json"
    if [ ! -f "$adc_file" ]; then
        echo "Error: No Application Default Credentials found."
        exit 1
    fi
    
    CLIENT_ID=$(jq -r '.client_id' "$adc_file")
    CLIENT_SECRET=$(jq -r '.client_secret' "$adc_file")
    REFRESH_TOKEN=$(jq -r '.refresh_token' "$adc_file")
    
    TOKEN_RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
        -d "client_id=$CLIENT_ID" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "refresh_token=$REFRESH_TOKEN" \
        -d "grant_type=refresh_token")
    
    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
    
    if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
        echo "Error: Failed to get access token"
        echo "$TOKEN_RESPONSE"
        exit 1
    fi
    
    echo "$ACCESS_TOKEN"
}

# Get list of verified sites
get_verified_sites() {
    local token=$1
    echo "Fetching your verified sites from Google Search Console..."
    echo ""
    
    RESPONSE=$(curl -s -X GET \
        "https://www.googleapis.com/webmasters/v3/sites" \
        -H "Authorization: Bearer $token")
    
    # Save response for debugging
    echo "$RESPONSE" > search_console_sites.json
    
    # Check if we got sites
    if echo "$RESPONSE" | jq -e '.siteEntry' > /dev/null 2>&1; then
        echo "Found the following verified sites:"
        echo "-----------------------------------"
        echo "$RESPONSE" | jq -r '.siteEntry[] | "- \(.siteUrl) (Permission: \(.permissionLevel))"'
        echo ""
        
        # Extract just the URLs for further processing
        echo "$RESPONSE" | jq -r '.siteEntry[].siteUrl' > verified_sites.txt
        return 0
    else
        echo "No sites found or error accessing Search Console:"
        echo "$RESPONSE" | jq .
        return 1
    fi
}

# Check site performance data
check_site_performance() {
    local token=$1
    local site_url=$2
    local encoded_url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$site_url'))")
    
    echo "Checking performance for: $site_url"
    
    # Get search analytics data for the last 7 days
    local end_date=$(date +%Y-%m-%d)
    local start_date=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d)
    
    PERF_DATA=$(curl -s -X POST \
        "https://www.googleapis.com/webmasters/v3/sites/$encoded_url/searchAnalytics/query" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"startDate\": \"$start_date\",
            \"endDate\": \"$end_date\",
            \"dimensions\": [\"page\"],
            \"rowLimit\": 10
        }")
    
    if echo "$PERF_DATA" | jq -e '.rows' > /dev/null 2>&1; then
        local total_clicks=$(echo "$PERF_DATA" | jq '[.rows[].clicks] | add // 0')
        local total_impressions=$(echo "$PERF_DATA" | jq '[.rows[].impressions] | add // 0')
        echo "  Last 7 days: $total_clicks clicks, $total_impressions impressions"
        
        # Save detailed data
        echo "$PERF_DATA" > "performance_${site_url//[^a-zA-Z0-9]/_}.json"
    else
        echo "  No performance data available"
    fi
}

# Main execution
echo "Getting access token..."
ACCESS_TOKEN=$(get_token)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Failed to get access token"
    exit 1
fi

echo "Token obtained successfully!"
echo ""

# Get all verified sites
if get_verified_sites "$ACCESS_TOKEN"; then
    echo "Checking performance data for each site..."
    echo "=========================================="
    
    # Read sites and check each one
    while IFS= read -r site_url; do
        if [ ! -z "$site_url" ]; then
            check_site_performance "$ACCESS_TOKEN" "$site_url"
            echo ""
        fi
    done < verified_sites.txt
    
    echo ""
    echo "Site data saved to:"
    echo "- search_console_sites.json (all sites)"
    echo "- performance_*.json (individual site data)"
    echo "- verified_sites.txt (list of URLs)"
else
    echo "Could not retrieve sites from Search Console"
fi