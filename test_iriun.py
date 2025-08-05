"""
Quick test for Iriun Webcam functionality
"""

import cv2
import time

def test_iriun_webcam():
    print("🔍 Testing Iriun Webcam (Camera 2)...")
    print("Make sure your phone app is connected!")
    print("Press 'q' to quit")
    
    cap = cv2.VideoCapture(2)
    
    if not cap.isOpened():
        print("❌ Could not open Iriun Webcam (Camera 2)")
        print("💡 Make sure:")
        print("   1. Iriun Webcam service is running: /usr/local/bin/iriunwebcam")
        print("   2. Your phone has Iriun Webcam app installed and connected")
        print("   3. Both devices are on the same WiFi network")
        return False
    
    # Set higher resolution for better QR detection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    print("✅ Iriun Webcam opened successfully!")
    print(f"Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Could not read frame")
            break
        
        frame_count += 1
        
        # Add overlay
        cv2.putText(frame, f"Iriun Webcam - Frame {frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "High-res camera for QR detection", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Iriun Webcam Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    test_iriun_webcam()
