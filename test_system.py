"""
Test script for Smart Attendance System
Verifies that all components are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import pytesseract
        print("✅ PyTesseract imported successfully")
    except ImportError as e:
        print(f"❌ PyTesseract import failed: {e}")
        return False
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        print("✅ Google API packages imported successfully")
    except ImportError as e:
        print(f"❌ Google API packages import failed: {e}")
        return False
    
    try:
        import tkinter as tk
        print("✅ Tkinter imported successfully")
    except ImportError as e:
        print(f"❌ Tkinter import failed: {e}")
        return False
    
    return True

def test_tesseract():
    """Test Tesseract OCR installation"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract test failed: {e}")
        print("Please install Tesseract OCR:")
        print("Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("Fedora: sudo dnf install tesseract")
        return False

def test_camera():
    """Test camera access"""
    print("\nTesting camera access...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera access successful")
                print(f"   Frame size: {frame.shape}")
            else:
                print("❌ Could not read frame from camera")
                return False
            cap.release()
            return True
        else:
            print("❌ Could not open camera")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_credentials():
    """Test Google Sheets credentials"""
    print("\nTesting Google Sheets credentials...")
    
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found")
        print("Please follow GOOGLE_SHEETS_SETUP.md to create credentials")
        return False
    
    try:
        import json
        from google.oauth2 import service_account
        
        with open("credentials.json", "r") as f:
            creds_data = json.load(f)
        
        if "client_email" in creds_data:
            print(f"✅ Credentials file valid")
            print(f"   Service account: {creds_data['client_email']}")
            return True
        else:
            print("❌ Invalid credentials file format")
            return False
            
    except Exception as e:
        print(f"❌ Credentials test failed: {e}")
        return False

def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")
    
    try:
        import config
        
        if config.SHEET_ID == "your_google_sheet_id_here":
            print("⚠️  SHEET_ID not configured in config.py")
            print("   Please update SHEET_ID with your actual Google Sheet ID")
            return False
        else:
            print("✅ Configuration looks good")
            print(f"   Sheet ID: {config.SHEET_ID[:20]}...")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Smart Attendance System Test ===\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Tesseract OCR", test_tesseract),
        ("Camera Access", test_camera),
        ("Google Credentials", test_credentials),
        ("Configuration", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print(f"\n=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo run the application:")
        print("python main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the application.")
        
        if passed < 2:  # Critical failures
            print("\nCritical issues detected. Please run setup.sh first:")
            print("chmod +x setup.sh && ./setup.sh")

if __name__ == "__main__":
    main()
