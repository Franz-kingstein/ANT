#!/bin/bash

# Smart Attendance System Setup Script

echo "=== Smart Attendance System Setup ==="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv attendance_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source attendance_env/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Install Tesseract OCR
echo "🔧 Installing Tesseract OCR..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    echo "Detected Ubuntu/Debian system"
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    echo "Detected CentOS/RHEL system"
    sudo yum install -y tesseract tesseract-devel
elif command -v dnf &> /dev/null; then
    # Fedora
    echo "Detected Fedora system"
    sudo dnf install -y tesseract tesseract-devel
else
    echo "⚠️  Could not detect package manager. Please install Tesseract OCR manually:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   Fedora: sudo dnf install tesseract"
    echo "   CentOS/RHEL: sudo yum install tesseract"
fi

# Test Tesseract installation
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR installed: $(tesseract --version | head -n1)"
else
    echo "❌ Tesseract OCR installation failed"
fi

echo
echo "=== Setup Instructions ==="
echo
echo "1. Google Sheets API Setup:"
echo "   - Go to https://console.cloud.google.com/"
echo "   - Create a new project or select existing one"
echo "   - Enable Google Sheets API"
echo "   - Create service account credentials"
echo "   - Download credentials.json and place it in this directory"
echo
echo "2. Create Google Sheet:"
echo "   - Create a new Google Sheet"
echo "   - Share it with the service account email (from credentials.json)"
echo "   - Copy the Sheet ID from the URL and update config.py"
echo
echo "3. Run the application:"
echo "   source attendance_env/bin/activate"
echo "   python main.py"
echo
echo "=== Setup Complete! ==="
