#!/bin/bash

echo "🚀 Starting Smart Attendance System deployment on Render..."

# Install system dependencies for barcode detection
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y libzbar0 libzbar-dev

# Upgrade pip and related tools
echo "🔧 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Try to install from minimal requirements first
echo "🐍 Installing dependencies from minimal requirements..."
if pip install -r requirements-minimal.txt; then
    echo "✅ Minimal requirements installed successfully"
else
    echo "⚠️ Minimal requirements failed, trying individual installs..."

    # Install critical packages
    pip install Flask==3.0.0
    pip install gunicorn==21.2.0
    pip install numpy==1.24.4
    pip install requests==2.31.0

    # Install OpenCV and fail loudly if missing
    echo "📷 Installing OpenCV..."
    if pip install opencv-python-headless==4.7.1.72; then
        echo "✅ OpenCV installed"
    else
        echo "❌ OpenCV installation failed – deployment cannot continue"
        exit 1
    fi

    # Try other optional dependencies
    pip install pyzbar==0.1.9 || echo "⚠️ pyzbar failed"
    pip install google-api-python-client==2.100.0 || echo "⚠️ Google API failed"
    pip install Pillow==9.5.0 || echo "⚠️ Pillow failed"
fi

# Verify gunicorn installation
echo "✅ Verifying gunicorn installation..."
if gunicorn --version; then
    echo "✅ Gunicorn is ready!"
else
    echo "❌ Gunicorn not found, installing as fallback..."
    pip install gunicorn --force-reinstall
fi

echo "✅ Build completed successfully!"
echo "🚀 Your Smart Attendance System is ready to deploy on Render!"
