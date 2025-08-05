"""
Utility functions for the Smart Attendance System
"""

import cv2
import numpy as np
import re
from datetime import datetime
import os

def preprocess_image_for_ocr(image):
    """
    Preprocess image for better OCR results
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Apply morphological operations to clean up
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def extract_region(image, region_config):
    """
    Extract a specific region from the image based on relative coordinates
    """
    height, width = image.shape[:2]
    
    x_start = int(region_config['x_start'] * width)
    x_end = int(region_config['x_end'] * width)
    y_start = int(region_config['y_start'] * height)
    y_end = int(region_config['y_end'] * height)
    
    return image[y_start:y_end, x_start:x_end]

def clean_extracted_text(text, text_type="general"):
    """
    Clean and validate extracted text
    """
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    if text_type == "name":
        # For names, keep only letters and spaces
        cleaned = re.sub(r'[^A-Za-z\s]', '', cleaned)
        # Remove extra spaces
        cleaned = ' '.join(cleaned.split())
        
    elif text_type == "regno":
        # For registration numbers, keep alphanumeric characters
        cleaned = re.sub(r'[^A-Za-z0-9]', '', cleaned)
        
    return cleaned.upper()

def validate_name(name):
    """
    Validate extracted name
    """
    if not name or len(name) < 3:
        return False
    
    # Check if name contains at least one letter
    if not re.search(r'[A-Za-z]', name):
        return False
        
    # Check if name is reasonable length
    if len(name) > 50:
        return False
        
    return True

def validate_regno(regno):
    """
    Validate registration number based on Karunya format
    STRICT: Only accepts URK format for Karunya Institute
    Expected format: URK23AI1112 (URK + 2 digits + 2 letters + 4 digits)
    """
    if not regno or len(regno) < 11:  # URK + 8 chars = 11 minimum
        return False
    
    # Must start with URK for Karunya Institute
    if not regno.startswith('URK'):
        return False
    
    # ONLY accept Karunya specific pattern: URK + 2 digits + 2 letters + 4 digits
    import re
    karunya_pattern = r'^URK\d{2}[A-Z]{2}\d{4}$'
    
    return bool(re.match(karunya_pattern, regno))

def get_current_timestamp():
    """
    Get current timestamp in readable format
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    """
    Get current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")

def save_debug_image(image, filename, folder="debug_images"):
    """
    Save image for debugging purposes
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filepath = os.path.join(folder, filename)
    cv2.imwrite(filepath, image)
    return filepath

def draw_detection_box(image, contour, color=(0, 255, 0), thickness=2):
    """
    Draw bounding box around detected card
    """
    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)
    return image

def draw_text_regions(image, name_region, regno_region):
    """
    Draw rectangles showing name and regno regions
    """
    height, width = image.shape[:2]
    
    # Name region (red)
    name_x1 = int(name_region['x_start'] * width)
    name_x2 = int(name_region['x_end'] * width)
    name_y1 = int(name_region['y_start'] * height)
    name_y2 = int(name_region['y_end'] * height)
    cv2.rectangle(image, (name_x1, name_y1), (name_x2, name_y2), (0, 0, 255), 2)
    cv2.putText(image, "NAME", (name_x1, name_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Regno region (green)
    regno_x1 = int(regno_region['x_start'] * width)
    regno_x2 = int(regno_region['x_end'] * width)
    regno_y1 = int(regno_region['y_start'] * height)
    regno_y2 = int(regno_region['y_end'] * height)
    cv2.rectangle(image, (regno_x1, regno_y1), (regno_x2, regno_y2), (0, 255, 0), 2)
    cv2.putText(image, "REGNO", (regno_x1, regno_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return image

def log_message(message, level="INFO"):
    """
    Log messages with timestamp
    """
    timestamp = get_current_timestamp()
    print(f"[{timestamp}] [{level}] {message}")

def calculate_aspect_ratio(contour):
    """
    Calculate aspect ratio of a contour
    """
    x, y, w, h = cv2.boundingRect(contour)
    return w / h if h > 0 else 0

def get_available_cameras():
    """
    Get list of available camera indices
    """
    available_cameras = []
    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

def test_camera_connection(camera_index):
    """
    Test if a specific camera is working
    Returns (is_working, resolution, fps)
    """
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        return False, None, None
    
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return False, None, None
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    cap.release()
    return True, (width, height), fps

def identify_camera_type(camera_index):
    """
    Identify the type of camera based on index and resolution
    """
    is_working, resolution, fps = test_camera_connection(camera_index)
    
    if not is_working:
        return "Unknown (Not Working)"
    
    width, height = resolution
    
    # Common camera identification patterns
    if camera_index == 0:
        return f"Built-in Webcam ({width}x{height})"
    elif camera_index == 1:
        return f"USB Webcam ({width}x{height})"
    elif camera_index == 2:
        if width >= 1280:  # High resolution typically means Iriun or similar
            return f"Iriun Webcam ({width}x{height})"
        else:
            return f"External Camera ({width}x{height})"
    else:
        return f"Camera {camera_index} ({width}x{height})"
