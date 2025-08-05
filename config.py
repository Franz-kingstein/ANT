import os  # add at top if missing

# Configuration settings for the Smart Attendance System

# Google Sheets Configuration  
SHEET_ID = "13D7-qytLtL5q_EIz11cu3MHP2-egRuxXddH7V3WKV7U"  # Replace with your actual Google Sheet ID from step 6
SHEET_NAME = "ANT"  # Name of the sheet tab
CREDENTIALS_FILE = "credentials.json"  # Google API credentials file

# Camera Configuration
CAMERA_INDEX = 2  # Iriun Webcam (high resolution for better QR detection)
# Alternative cameras: 0 = built-in webcam, 1 = USB webcam, 2 = Iriun Webcam
CAMERA_WIDTH = 1920  # Higher resolution for better QR code detection
CAMERA_HEIGHT = 1080
FPS = 30

# OCR Configuration
TESSERACT_CONFIG = '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '
CONFIDENCE_THRESHOLD = 20  # Further lowered for better detection

# Registration Number Validation
REQUIRED_REGNO_PREFIX = "URK"  # Registration numbers must start with URK for Karunya Institute
KARUNYA_REGNO_PATTERN = r'^URK\d{2}[A-Z]{2}\d{4}$'  # URK + 2 digits + 2 letters + 4 digits

# ID Card Detection
MIN_CARD_AREA = 8000   # Minimum area for card detection (much more lenient)
CARD_ASPECT_RATIO_MIN = 0.8  # Minimum aspect ratio for ID cards (very flexible)
CARD_ASPECT_RATIO_MAX = 3.0  # Maximum aspect ratio for ID cards (very flexible)

# Text Region Configuration (relative to card dimensions)
# These coordinates are based on the standard Karunya ID card layout
NAME_REGION = {
    'x_start': 0.05,  # 5% from left
    'x_end': 0.95,    # 95% from left  
    'y_start': 0.60,  # 60% from top (red box area)
    'y_end': 0.75     # 75% from top
}

REGNO_REGION = {
    'x_start': 0.15,  # 15% from left
    'x_end': 0.85,    # 85% from left
    'y_start': 0.75,  # 75% from top (green box area)
    'y_end': 0.85     # 85% from top
}

# UI Configuration
WINDOW_TITLE = "Smart Attendance System - Karunya Institute"
PREVIEW_WIDTH = 800
PREVIEW_HEIGHT = 600

# Attendance Rules
PREVENT_DUPLICATE_DAILY = True  # Prevent multiple entries per day
ATTENDANCE_TIMEOUT = 2  # Seconds to wait before allowing next scan (reduced for testing)

# Debug Mode
DEBUG_MODE = True  # Set to False in production
SAVE_DEBUG_IMAGES = True  # Save processed images for debugging

# Email reporting configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT   = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER   = os.environ.get('SMTP_USER', '')        # your SMTP username
SMTP_PASS   = os.environ.get('SMTP_PASS', '')        # your SMTP password or app password
TO_EMAIL    = os.environ.get('TO_EMAIL', '')         # recipient email for attendance reports
