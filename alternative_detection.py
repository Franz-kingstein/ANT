"""
Alternative detection method for challenging conditions
"""

import cv2
import numpy as np

def detect_card_alternative(frame):
    """
    Alternative card detection method that's more forgiving
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Use adaptive threshold instead of Canny
    binary = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for rectangular shapes
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 10000:  # Even more relaxed area requirement
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Very relaxed criteria
            if 0.8 <= aspect_ratio <= 3.0 and area > 10000:
                candidates.append((contour, area))
    
    return candidates

# This function can be integrated into the camera handler if needed
