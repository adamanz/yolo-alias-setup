#!/bin/bash
# Quick indexing submission tool

echo "Quick Indexing Tool"
echo "==================="
echo ""

# Common sites - update these with your actual domains
SITES=(
    "https://mysimplestack.com"
    "https://www.mysimplestack.com"
    "https://adama.bio" 
    "https://www.adama.bio"
    # Add more of your sites here
)

# Function to submit URL
submit_url() {
    local url=$1
    echo "Submitting: $url"
    ./gindex-simple submit "$url" 2>&1 | grep -E "(error|Error|Success|urlNotificationMetadata)"
    echo ""
}

# Menu
echo "What would you like to do?"
echo "1. Submit homepage of all known sites"
echo "2. Submit specific URL"
echo "3. Submit multiple URLs from file"
echo "4. Check indexing status of URL"
echo ""

read -p "Choice (1-4): " choice

case $choice in
    1)
        echo -e "\nSubmitting all known sites..."
        for site in "${SITES[@]}"; do
            submit_url "$site"
            sleep 1  # Rate limiting
        done
        ;;
    2)
        read -p "Enter URL to submit: " url
        submit_url "$url"
        ;;
    3)
        read -p "Enter filename with URLs: " filename
        if [ -f "$filename" ]; then
            while IFS= read -r url; do
                submit_url "$url"
                sleep 1
            done < "$filename"
        else
            echo "File not found: $filename"
        fi
        ;;
    4)
        read -p "Enter URL to check status: " url
        echo "Checking status for: $url"
        ./gindex-simple status "$url"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

echo -e "\nDone!"
echo "Check your results in Google Search Console:"
echo "https://search.google.com/search-console"