"""
Test script for QR code detection
Tests the QR processor functionality
"""

import cv2
import numpy as np
from qr_processor import QRProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_qr_detection():
    """Test QR code detection with camera"""
    print("Testing QR Code Detection")
    print("Hold your ID card with QR code visible to the camera")
    print("Press 'q' to quit")
    
    # Initialize camera and QR processor
    cap = cv2.VideoCapture(0)
    qr_processor = QRProcessor()
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame for QR codes
        regno, annotated_frame = qr_processor.process_frame_for_qr(frame)
        
        if regno:
            print(f"✅ Registration number detected: {regno}")
        
        # Display the frame
        cv2.imshow('QR Code Test', annotated_frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_qr_detection()
