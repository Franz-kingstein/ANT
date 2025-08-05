"""
QR Code Processor for Smart Attendance System
Handles QR code detection and extraction from camera frames
"""

import cv2
import numpy as np
from pyzbar import pyzbar
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QRProcessor:
    def __init__(self):
        """Initialize QR code processor"""
        self.last_detected_qr = None
        self.detection_count = 0
        self.required_detections = 3  # Require multiple detections for stability
        
    def preprocess_frame_for_qr(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for better QR code detection
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Preprocessed frame optimized for QR detection
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization to improve contrast
        equalized = cv2.equalizeHist(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
        
        return blurred
        
    def detect_qr_codes(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect QR codes and ALL barcodes in the frame
        
        Args:
            frame: Input frame (can be color or grayscale)
            
        Returns:
            List of detected codes with their data and positions
        """
        try:
            # Preprocess frame for better detection
            processed_frame = self.preprocess_frame_for_qr(frame)
            
            # Detect ALL types of barcodes/QR codes (not just QR)
            detected_codes = pyzbar.decode(processed_frame)
            
            results = []
            for code in detected_codes:
                # Extract code data
                code_data = code.data.decode('utf-8')
                code_type = code.type
                
                logger.info(f"Detected {code_type} code: '{code_data}'")
                
                # Get bounding box coordinates
                (x, y, w, h) = code.rect
                
                # Get polygon points (for drawing outline)
                points = code.polygon
                if len(points) == 4:
                    pts = np.array([(point.x, point.y) for point in points], dtype=np.int32)
                else:
                    # Fallback to rectangle if polygon is not available
                    pts = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=np.int32)
                
                results.append({
                    'data': code_data,
                    'type': code_type,
                    'rect': (x, y, w, h),
                    'polygon': pts
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error detecting codes: {e}")
            return []
    
    def extract_registration_number(self, qr_data: str) -> Optional[str]:
        """
        Extract registration number from QR code data
        
        Args:
            qr_data: Raw data from QR code
            
        Returns:
            Registration number if found, None otherwise
        """
        try:
            # QR code might contain just the registration number
            # or it might be in a JSON/structured format
            qr_data = qr_data.strip()
            
            logger.info(f"Raw QR data: '{qr_data}' (length: {len(qr_data)})")
            
            # ENHANCED: Fix common OCR/barcode reading errors
            # Replace common misread characters
            corrected_data = qr_data
            corrections = {
                '%': 'R',  # % often misread as R
                ',': '2',  # , often misread as 2
                '1': 'I',  # 1 might be I in some cases
                '0': 'O',  # 0 might be O
                '5': 'S',  # 5 might be S
                '8': 'B',  # 8 might be B
            }
            
            # Apply corrections only if original doesn't start with URK
            if not corrected_data.startswith('URK'):
                for wrong, correct in corrections.items():
                    corrected_data = corrected_data.replace(wrong, correct)
                logger.info(f"After corrections: '{corrected_data}'")
            
            # Check if corrected data starts with URK
            if corrected_data.startswith('URK'):
                # Validate the format: URK + 2 digits + 2 letters + 4 digits
                import re
                urk_pattern = r'^URK\d{2}[A-Z]{2}\d{4}$'
                if re.match(urk_pattern, corrected_data):
                    logger.info(f"Valid URK format found: {corrected_data}")
                    return corrected_data
            
            # Check if it's directly a registration number (starts with URK)
            if qr_data.startswith('URK'):
                return qr_data
            
            # Try to parse as JSON in case it's structured data
            import json
            try:
                data_dict = json.loads(qr_data)
                # Look for common field names that might contain registration number
                possible_fields = ['regno', 'reg_no', 'registration_number', 'id', 'student_id']
                for field in possible_fields:
                    if field in data_dict and str(data_dict[field]).startswith('URK'):
                        return str(data_dict[field])
            except json.JSONDecodeError:
                pass
            
            # If it's plain text, try to find URK pattern with corrections
            import re
            urk_pattern = r'URK\d{2}[A-Z]{2}\d{4}'
            
            # First try original data
            match = re.search(urk_pattern, qr_data)
            if match:
                return match.group()
                
            # Try with corrections
            match = re.search(urk_pattern, corrected_data)
            if match:
                return match.group()
            
            logger.warning(f"Could not extract registration number from QR data: {qr_data}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting registration number from QR data: {e}")
            return None
    
    def process_frame_for_qr(self, frame: np.ndarray) -> Tuple[Optional[str], np.ndarray]:
        """
        Process frame to detect QR codes and extract registration numbers
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Tuple of (registration_number, annotated_frame)
        """
        annotated_frame = frame.copy()
        
        try:
            # Detect QR codes
            qr_codes = self.detect_qr_codes(frame)
            
            # Process each detected QR code
            for qr_code in qr_codes:
                # Draw QR code outline
                cv2.polylines(annotated_frame, [qr_code['polygon']], True, (0, 255, 0), 3)
                
                # Extract registration number
                regno = self.extract_registration_number(qr_code['data'])
                
                if regno:
                    # Validate registration number format
                    from utils import validate_regno
                    if validate_regno(regno):
                        # Add text annotation
                        x, y, w, h = qr_code['rect']
                        cv2.putText(annotated_frame, f"QR: {regno}", (x, y - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Stability check - require multiple consistent detections
                        if self.last_detected_qr == regno:
                            self.detection_count += 1
                        else:
                            self.last_detected_qr = regno
                            self.detection_count = 1
                        
                        # Return if we have enough consistent detections
                        if self.detection_count >= self.required_detections:
                            logger.info(f"Stable QR detection: {regno}")
                            self.detection_count = 0  # Reset for next detection
                            return regno, annotated_frame
                    else:
                        # Invalid registration number format
                        x, y, w, h = qr_code['rect']
                        cv2.putText(annotated_frame, f"Invalid: {regno}", (x, y - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    # Could not extract registration number
                    x, y, w, h = qr_code['rect']
                    cv2.putText(annotated_frame, "QR: No RegNo", (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Add status text
            status_text = f"QR Codes: {len(qr_codes)}"
            if self.last_detected_qr:
                status_text += f" | Last: {self.last_detected_qr} ({self.detection_count}/{self.required_detections})"
            
            cv2.putText(annotated_frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return None, annotated_frame
            
        except Exception as e:
            logger.error(f"Error processing frame for QR codes: {e}")
            # Add error status to frame
            cv2.putText(annotated_frame, f"QR Error: {str(e)[:30]}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return None, annotated_frame
    
    def reset_detection(self):
        """Reset detection state"""
        self.last_detected_qr = None
        self.detection_count = 0
        logger.info("QR detection state reset")
