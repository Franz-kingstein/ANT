#!/bin/bash

# Smart Attendance System Launcher

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "attendance_env" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate virtual environment
source attendance_env/bin/activate

# Check if credentials exist
if [ ! -f "credentials.json" ]; then
    echo "❌ credentials.json not found!"
    echo "Please follow the Google Sheets setup instructions in GOOGLE_SHEETS_SETUP.md"
    exit 1
fi

# Check if configuration is updated
if grep -q "your_google_sheet_id_here" config.py; then
    echo "❌ Please update SHEET_ID in config.py with your actual Google Sheet ID"
    exit 1
fi

# Run the application
echo "🚀 Starting Smart Attendance System..."
python main.py
