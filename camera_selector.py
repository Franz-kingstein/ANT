"""
Camera Selection Utility for Smart Attendance System
Helps test and select the best camera for the attendance system
"""

import cv2
import numpy as np
import time

def test_camera(camera_index):
    """Test a specific camera and show its feed"""
    print(f"\n🎥 Testing Camera {camera_index}")
    print("Press 'q' to quit this camera test")
    print("Press 'n' to try next camera")
    print("-" * 50)
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ Camera {camera_index} could not be opened")
        return False
    
    # Get camera info
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    print(f"✅ Camera {camera_index} opened successfully")
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    
    # Set desired resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    camera_working = False
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"❌ Could not read frame from camera {camera_index}")
            break
        
        camera_working = True
        frame_count += 1
        
        # Add overlay text
        cv2.putText(frame, f"Camera {camera_index} - Frame {frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 'n' for next camera", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Hold your ID card to test QR/text detection", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Show frame
        cv2.imshow(f'Camera {camera_index} Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if camera_working:
        print(f"✅ Camera {camera_index} is working properly")
    else:
        print(f"❌ Camera {camera_index} had issues")
    
    return camera_working

def detect_available_cameras():
    """Detect all available cameras on the system"""
    print("🔍 Detecting available cameras...")
    available_cameras = []
    
    # Check cameras 0-10 (should cover most cases)
    for i in range(11):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"✅ Camera {i} detected")
            cap.release()
        else:
            # Don't print for non-existent cameras to reduce noise
            pass
    
    return available_cameras

def get_camera_info(camera_index):
    """Get detailed information about a camera"""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return None
    
    info = {
        'index': camera_index,
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': int(cap.get(cv2.CAP_PROP_FPS)),
        'backend': cap.getBackendName() if hasattr(cap, 'getBackendName') else 'Unknown'
    }
    
    cap.release()
    return info

def main():
    """Main camera selection interface"""
    print("🎯 Smart Attendance System - Camera Selection Utility")
    print("=" * 60)
    
    # Detect available cameras
    cameras = detect_available_cameras()
    
    if not cameras:
        print("❌ No cameras detected!")
        return
    
    print(f"\n📱 Found {len(cameras)} camera(s): {cameras}")
    
    # Show camera details
    print("\n📋 Camera Details:")
    for cam_idx in cameras:
        info = get_camera_info(cam_idx)
        if info:
            print(f"   Camera {cam_idx}: {info['width']}x{info['height']} @ {info['fps']}fps ({info['backend']})")
    
    # Identify camera types
    print("\n🎥 Camera Types (typical):")
    print("   Camera 0: Built-in webcam")
    print("   Camera 1: USB webcam") 
    print("   Camera 2: Iriun Webcam (if installed)")
    
    print("\n" + "=" * 60)
    print("📱 Testing cameras one by one...")
    print("   Use this to see which camera works best for your ID card scanning")
    print("=" * 60)
    
    # Test each camera
    for cam_idx in cameras:
        user_input = input(f"\n🎥 Test Camera {cam_idx}? (y/n/q): ").lower().strip()
        
        if user_input == 'q':
            break
        elif user_input == 'y' or user_input == '':
            if test_camera(cam_idx):
                recommend = input(f"\n✅ Camera {cam_idx} working well. Use this for attendance? (y/n): ").lower().strip()
                if recommend == 'y':
                    print(f"\n🎯 Recommended: Update config.py to use CAMERA_INDEX = {cam_idx}")
                    print("   The attendance system will now use this camera.")
                    break
    
    print("\n✅ Camera selection complete!")
    print("💡 Tip: Iriun Webcam (usually Camera 2) often provides the best quality for QR code detection")

if __name__ == "__main__":
    main()
