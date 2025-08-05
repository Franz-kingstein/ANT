"""
Camera Handler for Smart Attendance System
Handles camera initialization, frame capture, and ID card detection
"""

import cv2
import numpy as np
from utils import log_message, draw_detection_box, calculate_aspect_ratio, save_debug_image
import config

class CameraHandler:
    def __init__(self):
        self.cap = None
        self.is_initialized = False
        
    def initialize_camera(self):
        """Initialize camera with specified settings"""
        try:
            self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
            
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, config.FPS)
            
            self.is_initialized = True
            log_message("Camera initialized successfully")
            return True
            
        except Exception as e:
            log_message(f"Failed to initialize camera: {str(e)}", "ERROR")
            return False
    
    def capture_frame(self):
        """Capture a single frame from camera"""
        if not self.is_initialized or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            log_message("Failed to capture frame", "WARNING")
            return None
    
    def detect_id_card(self, frame):
        """
        Detect ID card in the frame using contour detection
        Returns the largest rectangular contour that matches ID card characteristics
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edged = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours for potential ID cards
        card_candidates = []
        
        for contour in contours:
            # Calculate area
            area = cv2.contourArea(contour)
            
            # Skip very small contours
            if area < config.MIN_CARD_AREA:
                continue
            
            # Calculate aspect ratio
            aspect_ratio = calculate_aspect_ratio(contour)
            
            # Much more flexible criteria - just check basic size and ratio
            if (config.CARD_ASPECT_RATIO_MIN <= aspect_ratio <= config.CARD_ASPECT_RATIO_MAX):
                card_candidates.append((contour, area))
                
            # If we're being very lenient, also accept any reasonably large rectangular contour
            elif area > config.MIN_CARD_AREA * 1.5:  # 50% larger than minimum
                # Check if it's roughly rectangular using bounding box
                x, y, w, h = cv2.boundingRect(contour)
                rect_area = w * h
                extent = area / rect_area
                
                # If the contour fills most of its bounding rectangle, it's probably rectangular
                if extent > 0.6:  # At least 60% of bounding rectangle is filled
                    card_candidates.append((contour, area))
        
        # Return the largest card candidate
        if card_candidates:
            # Sort by area and return the largest
            largest_card = max(card_candidates, key=lambda x: x[1])
            return largest_card[0]
        
        return None
    
    def extract_card_region(self, frame, contour):
        """
        Extract the ID card region from the frame using perspective transformation
        """
        # Get the four corner points of the card
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) != 4:
            # Fallback: use bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            return frame[y:y+h, x:x+w]
        
        # Sort points in order: top-left, top-right, bottom-right, bottom-left
        points = approx.reshape(4, 2)
        sorted_points = self._sort_points(points)
        
        # Calculate dimensions for the straightened card
        width = max(
            np.linalg.norm(sorted_points[0] - sorted_points[1]),
            np.linalg.norm(sorted_points[2] - sorted_points[3])
        )
        height = max(
            np.linalg.norm(sorted_points[0] - sorted_points[3]),
            np.linalg.norm(sorted_points[1] - sorted_points[2])
        )
        
        # Define destination points for perspective transformation
        dst_points = np.array([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ], dtype=np.float32)
        
        # Perform perspective transformation
        matrix = cv2.getPerspectiveTransform(sorted_points.astype(np.float32), dst_points)
        straightened = cv2.warpPerspective(frame, matrix, (int(width), int(height)))
        
        if config.DEBUG_MODE and config.SAVE_DEBUG_IMAGES:
            save_debug_image(straightened, f"card_extracted_{cv2.getTickCount()}.jpg")
        
        return straightened
    
    def _sort_points(self, points):
        """
        Sort points in clockwise order starting from top-left
        """
        # Sort by x-coordinate
        x_sorted = points[np.argsort(points[:, 0]), :]
        
        # Get left and right points
        left = x_sorted[:2, :]
        right = x_sorted[2:, :]
        
        # Sort left points by y-coordinate (top-left, bottom-left)
        left = left[np.argsort(left[:, 1]), :]
        top_left, bottom_left = left
        
        # Sort right points by y-coordinate (top-right, bottom-right)
        right = right[np.argsort(right[:, 1]), :]
        top_right, bottom_right = right
        
        return np.array([top_left, top_right, bottom_right, bottom_left])
    
    def resize_frame_for_display(self, frame):
        """
        Resize frame for display in the GUI
        """
        height, width = frame.shape[:2]
        
        # Calculate scaling factor to fit preview dimensions
        scale_w = config.PREVIEW_WIDTH / width
        scale_h = config.PREVIEW_HEIGHT / height
        scale = min(scale_w, scale_h)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(frame, (new_width, new_height))
    
    def release_camera(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            log_message("Camera released")
    
    def __del__(self):
        """Destructor to ensure camera is released"""
        self.release_camera()
