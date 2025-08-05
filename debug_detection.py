#!/usr/bin/env python3
"""
Debug script to test ID card detection
"""

import cv2
import numpy as np
import sys
import os

# Add the project directory to Python path
sys.path.append('/home/franz/Documents/attendance')

from camera_handler import CameraHandler
import config

def debug_detection():
    """Debug the card detection process"""
    
    print("=== ID Card Detection Debug ===")
    print(f"MIN_CARD_AREA: {config.MIN_CARD_AREA}")
    print(f"ASPECT_RATIO_RANGE: {config.CARD_ASPECT_RATIO_MIN} - {config.CARD_ASPECT_RATIO_MAX}")
    print()
    
    # Initialize camera
    camera = CameraHandler()
    if not camera.initialize_camera():
        print("❌ Failed to initialize camera")
        return
    
    print("✅ Camera initialized. Press 'q' to quit, 's' to save current frame, 'd' to debug current frame")
    
    while True:
        # Capture frame
        frame = camera.capture_frame()
        if frame is None:
            continue
        
        # Create a copy for visualization
        debug_frame = frame.copy()
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        
        # Find all contours
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        print(f"\rFound {len(contours)} contours", end="", flush=True)
        
        # Analyze all contours
        card_candidates = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            if area > 5000:  # Show larger contours for debugging
                # Draw all significant contours in blue
                cv2.drawContours(debug_frame, [contour], -1, (255, 0, 0), 2)
                
                # Calculate aspect ratio
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Check if it meets area requirement
                if area >= config.MIN_CARD_AREA:
                    # Draw potential cards in yellow
                    cv2.drawContours(debug_frame, [contour], -1, (0, 255, 255), 3)
                    
                    # Check aspect ratio
                    if config.CARD_ASPECT_RATIO_MIN <= aspect_ratio <= config.CARD_ASPECT_RATIO_MAX:
                        # Check if it's rectangular (4 corners)
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) == 4:
                            # This is a valid card candidate - draw in green
                            cv2.drawContours(debug_frame, [contour], -1, (0, 255, 0), 4)
                            card_candidates.append(contour)
                            
                            # Add text info
                            cv2.putText(debug_frame, f"CARD: {area:.0f}px", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            # Wrong shape - draw in red
                            cv2.drawContours(debug_frame, [contour], -1, (0, 0, 255), 2)
                            cv2.putText(debug_frame, f"Shape:{len(approx)}", 
                                      (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    else:
                        # Wrong aspect ratio - draw in purple
                        cv2.drawContours(debug_frame, [contour], -1, (255, 0, 255), 2)
                        cv2.putText(debug_frame, f"AR:{aspect_ratio:.2f}", 
                                  (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                else:
                    # Too small - show area
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.putText(debug_frame, f"{area:.0f}", 
                              (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Add legend
        cv2.putText(debug_frame, "Blue: All contours | Yellow: Right size | Green: Valid cards", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(debug_frame, "Red: Wrong shape | Purple: Wrong ratio", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(debug_frame, f"Cards found: {len(card_candidates)}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show the debug frame
        cv2.imshow("Card Detection Debug", debug_frame)
        cv2.imshow("Edges", edged)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite("debug_frame.jpg", debug_frame)
            print("\n📸 Debug frame saved as debug_frame.jpg")
        elif key == ord('d'):
            print(f"\n=== Debug Info ===")
            print(f"Total contours: {len(contours)}")
            print(f"Card candidates: {len(card_candidates)}")
            print(f"Frame size: {frame.shape}")
            print(f"Settings: MIN_AREA={config.MIN_CARD_AREA}, AR={config.CARD_ASPECT_RATIO_MIN}-{config.CARD_ASPECT_RATIO_MAX}")
    
    # Cleanup
    camera.release_camera()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    debug_detection()
