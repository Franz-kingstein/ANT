# Render.com Build Script
#!/bin/bash

echo "🚀 Starting Smart Attendance System deployment on Render..."

# Install system dependencies for barcode detection
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y libzbar0 libzbar-dev

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"ld Script
#!/bin/bash

echo "🚀 Starting Smart Attendance System deployment on Render..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y libzbar0 libzbar-dev

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-web.txt || pip install -r requirements.txt

echo "✅ Build completed successfully!"
