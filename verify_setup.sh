#!/bin/bash

echo "🔧 Google Sheets API Setup Verification"
echo "======================================"
echo

# Check if credentials.json exists
if [ -f "credentials.json" ]; then
    echo "✅ credentials.json found"
    
    # Extract client_email from credentials
    CLIENT_EMAIL=$(python3 -c "import json; print(json.load(open('credentials.json'))['client_email'])" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Valid JSON format"
        echo "📧 Service account email: $CLIENT_EMAIL"
        echo
        echo "🔗 IMPORTANT: Make sure you've shared your Google Sheet with:"
        echo "   $CLIENT_EMAIL"
        echo
    else
        echo "❌ Invalid JSON format in credentials.json"
        exit 1
    fi
else
    echo "❌ credentials.json not found!"
    echo
    echo "Please:"
    echo "1. Download your service account JSON key from Google Cloud Console"
    echo "2. Save it as 'credentials.json' in this directory"
    echo
    exit 1
fi

# Check if SHEET_ID is configured
if grep -q "PASTE_YOUR_SHEET_ID_HERE\|your_google_sheet_id_here" config.py; then
    echo "❌ SHEET_ID not configured in config.py"
    echo
    echo "Please:"
    echo "1. Open your Google Sheet"
    echo "2. Copy the Sheet ID from the URL"
    echo "3. Update SHEET_ID in config.py"
    echo
    exit 1
else
    echo "✅ SHEET_ID configured in config.py"
fi

echo "🎉 Google Sheets API setup looks good!"
echo
echo "Next steps:"
echo "1. Run: python test_system.py"
echo "2. If all tests pass, run: ./run.sh"
