"""
OCR Processor for Smart Attendance System
Handles text extraction from ID card regions using Tesseract OCR
"""

import pytesseract
import cv2
from utils import (
    preprocess_image_for_ocr, extract_region, clean_extracted_text,
    validate_name, validate_regno, log_message, save_debug_image
)
import config

class OCRProcessor:
    def __init__(self):
        self.tesseract_config = config.TESSERACT_CONFIG
        
    def extract_text_from_card(self, card_image):
        """
        Extract name and registration number from ID card
        Returns tuple (name, regno, confidence_scores)
        """
        try:
            # Extract name region
            name_region = extract_region(card_image, config.NAME_REGION)
            name_text, name_confidence = self._extract_text_from_region(
                name_region, "name"
            )
            
            # Extract registration number region
            regno_region = extract_region(card_image, config.REGNO_REGION)
            regno_text, regno_confidence = self._extract_text_from_region(
                regno_region, "regno"
            )
            
            if config.DEBUG_MODE and config.SAVE_DEBUG_IMAGES:
                timestamp = cv2.getTickCount()
                save_debug_image(name_region, f"name_region_{timestamp}.jpg")
                save_debug_image(regno_region, f"regno_region_{timestamp}.jpg")
            
            return name_text, regno_text, (name_confidence, regno_confidence)
            
        except Exception as e:
            log_message(f"Error in text extraction: {str(e)}", "ERROR")
            return None, None, (0, 0)
    
    def _extract_text_from_region(self, region_image, text_type):
        """
        Extract text from a specific region with preprocessing
        """
        if region_image is None or region_image.size == 0:
            return "", 0
        
        try:
            # Preprocess the image for better OCR
            processed = preprocess_image_for_ocr(region_image)
            
            # Resize for better OCR if image is too small
            height, width = processed.shape
            if height < 50 or width < 100:
                scale = max(50/height, 100/width, 2.0)
                new_width = int(width * scale)
                new_height = int(height * scale)
                processed = cv2.resize(processed, (new_width, new_height), 
                                     interpolation=cv2.INTER_CUBIC)
            
            # Apply additional preprocessing based on text type
            if text_type == "name":
                processed = self._preprocess_for_name(processed)
            elif text_type == "regno":
                processed = self._preprocess_for_regno(processed)
            
            # Extract text using Tesseract
            data = pytesseract.image_to_data(
                processed, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Filter results by confidence
            texts = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > config.CONFIDENCE_THRESHOLD:
                    text = data['text'][i].strip()
                    if text:
                        texts.append(text)
                        confidences.append(int(data['conf'][i]))
            
            # Combine all text
            combined_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Clean the extracted text
            cleaned_text = clean_extracted_text(combined_text, text_type)
            
            # Validate the text
            if text_type == "name" and not validate_name(cleaned_text):
                log_message(f"Invalid name extracted: '{cleaned_text}'", "WARNING")
                return "", 0
            elif text_type == "regno" and not validate_regno(cleaned_text):
                log_message(f"Invalid regno extracted: '{cleaned_text}'", "WARNING")
                return "", 0
            
            log_message(f"Extracted {text_type}: '{cleaned_text}' (confidence: {avg_confidence:.1f})")
            return cleaned_text, avg_confidence
            
        except Exception as e:
            log_message(f"Error extracting {text_type}: {str(e)}", "ERROR")
            return "", 0
    
    def _preprocess_for_name(self, image):
        """
        Additional preprocessing specific to name region
        """
        # Apply morphological opening to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
        opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        
        # Dilate to make text thicker
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        dilated = cv2.dilate(opened, kernel, iterations=1)
        
        return dilated
    
    def _preprocess_for_regno(self, image):
        """
        Additional preprocessing specific to registration number region
        """
        # Apply morphological closing to connect broken characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # Apply median blur to reduce noise while preserving edges
        blurred = cv2.medianBlur(closed, 3)
        
        return blurred
    
    def extract_text_fallback(self, card_image):
        """
        Fallback method: extract text from entire card if region-based fails
        """
        try:
            # Preprocess entire card
            processed = preprocess_image_for_ocr(card_image)
            
            # Extract all text
            extracted_text = pytesseract.image_to_string(
                processed, 
                config=self.tesseract_config
            )
            
            # Try to find name and regno patterns in the extracted text
            lines = extracted_text.split('\n')
            
            name = None
            regno = None
            
            for line in lines:
                cleaned_line = clean_extracted_text(line)
                
                # Look for registration number pattern
                if validate_regno(cleaned_line) and regno is None:
                    regno = cleaned_line
                
                # Look for name (longer text that's not regno)
                elif validate_name(cleaned_line) and name is None and len(cleaned_line) > 5:
                    name = cleaned_line
            
            log_message(f"Fallback extraction - Name: '{name}', Regno: '{regno}'")
            return name, regno, (50, 50)  # Lower confidence for fallback
            
        except Exception as e:
            log_message(f"Fallback extraction failed: {str(e)}", "ERROR")
            return None, None, (0, 0)
    
    def is_text_extraction_successful(self, name, regno, confidences):
        """
        Check if text extraction was successful
        """
        name_conf, regno_conf = confidences
        
        # Both name and regno should be extracted with reasonable confidence
        return (
            name and regno and 
            validate_name(name) and validate_regno(regno) and
            name_conf >= config.CONFIDENCE_THRESHOLD and 
            regno_conf >= config.CONFIDENCE_THRESHOLD
        )
