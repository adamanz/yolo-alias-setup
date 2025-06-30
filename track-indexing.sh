#!/bin/bash
# Track indexing progress

echo "Indexing Progress Tracker"
echo "========================"
echo "Date: $(date)"
echo ""

SITES=(
    "mysimplestack.com"
    "simple.company"
    "thesimple.co"
    "castit.ai"
    "textmaya.ai"
    "goodseeds.club"
)

for site in "${SITES[@]}"; do
    echo "Checking $site..."
    
    # Check if indexed in Google
    indexed=$(curl -s "https://www.google.com/search?q=site:$site" | grep -c "result")
    
    if [ $indexed -gt 0 ]; then
        echo "  ✅ Found in Google index"
    else
        echo "  ❌ Not found in Google index"
    fi
    
    # Check HTTP status
    status=$(curl -s -o /dev/null -w "%{http_code}" "https://$site")
    echo "  HTTP Status: $status"
    echo ""
done

echo "Run 'python3 search-console-check.py' for detailed metrics"