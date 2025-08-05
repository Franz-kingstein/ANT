"""
Main application for Smart Attendance System
QR CODE ONLY MODE - OCR processing disabled
"""

import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time

from camera_handler import CameraHandler
# from ocr_processor import OCRProcessor  # DISABLED - QR ONLY MODE
from qr_processor import QRProcessor
from sheets_manager import SheetsManager
from utils import log_message, draw_detection_box, draw_text_regions, get_current_timestamp
import config

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry("1000x800")
        
        # Initialize components - QR ONLY MODE
        self.camera = CameraHandler()
        # self.ocr = OCRProcessor()  # DISABLED - QR ONLY MODE
        self.qr_processor = QRProcessor()
        self.sheets = SheetsManager()
        
        # Application state
        self.is_running = False
        self.last_scan_time = 0
        self.processing = False
        
        # Setup GUI
        self.setup_gui()
        
        # Initialize systems
        self.initialize_systems()
    
    def setup_gui(self):
        """Setup the graphical user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Smart Attendance System", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Camera frame
        camera_frame = ttk.LabelFrame(main_frame, text="Camera Preview", padding="5")
        camera_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Video label
        self.video_label = ttk.Label(camera_frame, text="Camera not initialized")
        self.video_label.pack(expand=True)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start Camera", 
                                      command=self.start_camera)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Camera", 
                                     command=self.stop_camera, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.manual_scan_button = ttk.Button(control_frame, text="Manual Scan", 
                                           command=self.manual_scan, state=tk.DISABLED)
        self.manual_scan_button.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # Status labels
        self.status_label = ttk.Label(status_frame, text="System: Not Ready", 
                                     font=("Arial", 10, "bold"))
        self.status_label.pack(anchor=tk.W)
        
        self.last_scan_label = ttk.Label(status_frame, text="Last Scan: None")
        self.last_scan_label.pack(anchor=tk.W)
        
        self.attendance_count_label = ttk.Label(status_frame, text="Today's Attendance: 0")
        self.attendance_count_label.pack(anchor=tk.W)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="5")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_text = """
Instructions:
1. Click 'Start Camera' to begin
2. Hold your ID card in front of the camera
3. Keep the card steady and well-lit
4. The system will automatically detect and process the card
5. Attendance will be marked in the Google Sheet

Tips:
• Ensure good lighting
• Hold card flat and straight
• Wait for processing to complete before moving
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # Google Sheets link frame
        link_frame = ttk.Frame(main_frame)
        link_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.sheets_link_button = ttk.Button(link_frame, text="Open Google Sheet", 
                                           command=self.open_google_sheet, 
                                           state=tk.DISABLED)
        self.sheets_link_button.pack()
    
    def initialize_systems(self):
        """Initialize camera, OCR, and Google Sheets"""
        log_message("Initializing systems...")
        
        # Initialize Google Sheets first
        if self.sheets.initialize_sheets_api():
            self.sheets_link_button.config(state=tk.NORMAL)
            self.update_status("Google Sheets: Connected")
        else:
            self.update_status("Google Sheets: Failed to connect")
            messagebox.showerror("Error", 
                               "Failed to connect to Google Sheets. Please check your credentials.")
        
        # Initialize camera
        if self.camera.initialize_camera():
            self.start_button.config(state=tk.NORMAL)
            self.update_status("System: Ready")
        else:
            self.update_status("Camera: Failed to initialize")
            messagebox.showerror("Error", 
                               "Failed to initialize camera. Please check your camera connection.")
    
    def start_camera(self):
        """Start camera preview and processing"""
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.manual_scan_button.config(state=tk.NORMAL)
        
        # Start video thread
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
        
        self.update_status("Camera: Running")
        log_message("Camera started")
    
    def stop_camera(self):
        """Stop camera preview and processing"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.manual_scan_button.config(state=tk.DISABLED)
        
        # Clear video display
        self.video_label.config(image="", text="Camera stopped")
        
        self.update_status("Camera: Stopped")
        log_message("Camera stopped")
    
    def video_loop(self):
        """Main video processing loop"""
        while self.is_running:
            try:
                # Capture frame
                frame = self.camera.capture_frame()
                if frame is None:
                    continue
                
                # Process frame for display with QR detection overlay
                display_frame = frame.copy()
                
                # Try to detect QR codes for visual feedback (non-blocking)
                try:
                    qr_codes = self.qr_processor.detect_qr_codes(frame)
                    for qr_code in qr_codes:
                        # Draw QR code outline
                        cv2.polylines(display_frame, [qr_code['polygon']], True, (0, 255, 255), 2)
                        x, y, w, h = qr_code['rect']
                        cv2.putText(display_frame, "QR Detected", (x, y - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                except:
                    pass  # Don't let QR detection errors stop video display
                
                # Add text overlay to show scanning status
                cv2.putText(display_frame, "Hold ID card steady - QR code preferred", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Check if enough time has passed since last scan for automatic processing
                current_time = time.time()
                if (current_time - self.last_scan_time) > config.ATTENDANCE_TIMEOUT and not self.processing:
                    # Process frame for text automatically (every few seconds)
                    if int(current_time) % 3 == 0:  # Try every 3 seconds
                        threading.Thread(target=self.process_frame_for_text, args=(frame,), daemon=True).start()
                
                # Convert frame for display
                self.display_frame(display_frame)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                log_message(f"Error in video loop: {str(e)}", "ERROR")
                time.sleep(0.1)
    
    def display_frame(self, frame):
        """Display frame in the GUI"""
        try:
            # Resize frame for display
            display_frame = self.camera.resize_frame_for_display(frame)
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # Keep a reference
            
        except Exception as e:
            log_message(f"Error displaying frame: {str(e)}", "WARNING")
    
    def manual_scan(self):
        """Manually trigger card scanning"""
        if not self.is_running or self.processing:
            return
        
        # Capture current frame
        frame = self.camera.capture_frame()
        if frame is None:
            messagebox.showwarning("Warning", "Could not capture frame from camera")
            return
        
        # Try to detect card first (but don't require it)
        card_contour = self.camera.detect_id_card(frame)
        
        # Always process the frame for text, regardless of card detection
        log_message("Processing frame for text extraction")
        threading.Thread(target=self.process_frame_for_text, args=(frame,), daemon=True).start()
    
    def process_frame_for_text(self, frame):
        """Process frame using QR code scanning ONLY - OCR disabled"""
        if self.processing:
            return
        
        self.processing = True
        self.update_status("Scanning for QR code...")
        
        try:
            # ONLY QR code scanning - No OCR fallback
            log_message("Attempting QR code scanning...")
            regno_from_qr, qr_annotated_frame = self.qr_processor.process_frame_for_qr(frame)
            
            if regno_from_qr and self.validate_and_extract_name_from_qr(regno_from_qr, frame):
                return  # Successfully processed via QR code
            
            # No OCR fallback - QR code only mode
            log_message("QR scan unsuccessful - QR code only mode enabled")
            
            # Show QR-only message to user
            if not hasattr(self, '_qr_only_message_shown'):
                self._qr_only_message_shown = True
                self.root.after(0, lambda: messagebox.showinfo(
                    "QR Code Only Mode", 
                    "System is in QR code only mode.\n\nPlease ensure:\n• QR code is clearly visible\n• Good lighting conditions\n• Hold card steady\n• QR code is not damaged or dirty"
                ))
        
        except Exception as e:
            log_message(f"Error processing frame for QR codes: {str(e)}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror(
                "QR Processing Error", 
                f"Error processing QR codes: {str(e)}"
            ))
        
        finally:
            self.processing = False
            self.update_status("Ready for QR scan")
    
    def validate_and_extract_name_from_qr(self, regno_from_qr, frame):
        """Validate QR registration number and try to extract name from OCR"""
        try:
            from utils import validate_regno
            
            # Validate the registration number format
            if not validate_regno(regno_from_qr):
                log_message(f"Invalid registration number format from QR: {regno_from_qr}")
                return False
            
            log_message(f"Valid registration number from QR: {regno_from_qr}")
            
            # Try to extract name using OCR from the same frame
            name_from_ocr = self.extract_name_only(frame)
            
            if name_from_ocr:
                log_message(f"Found name via OCR: {name_from_ocr}")
                
                # Mark attendance with QR registration number and OCR name
                if self.sheets.mark_attendance(name_from_ocr, regno_from_qr):
                    self.last_scan_time = time.time()
                    self.update_status(f"Attendance marked: {name_from_ocr}")
                    self.last_scan_label.config(text=f"Last Scan: {name_from_ocr} ({regno_from_qr})")
                    self.update_attendance_count()
                    
                    # Show success message
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success", 
                        f"Attendance marked successfully!\n\nMethod: QR Code + OCR\nName: {name_from_ocr}\nRegNo: {regno_from_qr}\nTime: {get_current_timestamp()}"
                    ))
                    return True
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", 
                        "Failed to mark attendance in Google Sheets"
                    ))
                    return False
            else:
                # QR code worked but couldn't extract name
                # For now, let's use a placeholder name and let user correct it
                placeholder_name = f"QR_STUDENT_{regno_from_qr}"
                log_message(f"QR scan successful but name extraction failed. Using placeholder: {placeholder_name}")
                
                # Mark attendance with placeholder name
                if self.sheets.mark_attendance(placeholder_name, regno_from_qr):
                    self.last_scan_time = time.time()
                    self.update_status(f"Attendance marked: {placeholder_name}")
                    self.last_scan_label.config(text=f"Last Scan: {placeholder_name} ({regno_from_qr})")
                    self.update_attendance_count()
                    
                    # Show info message asking user to update name in sheets
                    self.root.after(0, lambda: messagebox.showinfo(
                        "QR Scan Successful", 
                        f"Registration number captured from QR code!\n\nName: {placeholder_name} (Please update in Google Sheets)\nRegNo: {regno_from_qr}\nTime: {get_current_timestamp()}\n\nThe attendance has been marked, but please update the name in the Google Sheets manually."
                    ))
                    return True
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", 
                        "Failed to mark attendance in Google Sheets"
                    ))
                    return False
                    
        except Exception as e:
            log_message(f"Error validating QR registration number: {str(e)}", "ERROR")
            return False
    
    def extract_name_only(self, frame):
        """Extract only the name from the frame using OCR"""
        try:
            import pytesseract
            from utils import preprocess_image_for_ocr, validate_name
            
            # Try multiple regions for name extraction
            height, width = frame.shape[:2]
            
            # Define regions where name might appear
            name_regions = [
                # Upper portion (names usually appear at the top)
                frame[height//6:height//2, width//6:5*width//6],
                # Center portion
                frame[height//4:3*height//4, width//4:3*width//4],
                # Full frame as last resort
                frame
            ]
            
            for i, region in enumerate(name_regions):
                if region.size == 0:
                    continue
                    
                log_message(f"Searching for name in region {i+1}")
                
                # Preprocess for better OCR
                processed = preprocess_image_for_ocr(region)
                
                # Extract text
                text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6')
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for line in lines:
                    # Skip lines that contain registration number patterns
                    if 'URK' in line.upper():
                        continue
                    
                    # Clean and validate potential name
                    cleaned_name = self.clean_name_text(line)
                    if cleaned_name and validate_name(cleaned_name):
                        log_message(f"Found valid name: {cleaned_name}")
                        return cleaned_name
            
            log_message("Could not extract name from frame")
            return None
            
        except Exception as e:
            log_message(f"Error extracting name: {str(e)}", "ERROR")
            return None
    
    def clean_name_text(self, text):
        """Clean and format name text extracted from OCR"""
        if not text:
            return None
        
        # Remove common OCR artifacts and unwanted characters
        import re
        
        # Remove special characters but keep spaces and hyphens
        cleaned = re.sub(r'[^A-Za-z\s\-\.]', '', text)
        
        # Remove common OCR mistakes
        cleaned = cleaned.replace('|', 'I').replace('0', 'O').replace('1', 'I')
        
        # Split into words and capitalize properly
        words = cleaned.split()
        formatted_words = []
        
        for word in words:
            if len(word) >= 2:  # Only keep words with 2+ characters
                formatted_words.append(word.capitalize())
        
        if len(formatted_words) >= 2:  # Need at least first and last name
            return ' '.join(formatted_words)
        
        return None
    
    # DISABLED - QR ONLY MODE
    # def extract_text_patterns(self, image):
    #     """Extract name and registration number using pattern matching"""
    #     try:
    #         import pytesseract
    #         from utils import preprocess_image_for_ocr, validate_name, validate_regno
    #         
    #         # Preprocess image for better OCR
    #         processed = preprocess_image_for_ocr(image)
    #         
    #         # Extract all text from the image
    #         text = pytesseract.image_to_string(processed, config='--oem 3 --psm 6')
    #         
    #         # Split into lines
    #         lines = [line.strip() for line in text.split('\n') if line.strip()]
    #         
    #         name = None
    #         regno = None
    #         
    #         for line in lines:
    #             line_upper = line.upper()
    #             
    #             # Look for registration number pattern (URK format ONLY for Karunya)
    #             import re
    #             regno_patterns = [
    #                 r'URK\d{2}[A-Z]{2}\d{4}',  # ONLY Karunya format (URK23AI1112)
    #             ]
    #             
    #             for pattern in regno_patterns:
    #                 match = re.search(pattern, line_upper)
    #                 if match and not regno:
    #                     potential_regno = match.group()
    #                     if validate_regno(potential_regno):
    #                         regno = potential_regno
    #                         log_message(f"Found Karunya regno: {regno}")
    #                         break
    #             
    #             # Look for name (longer text that's not regno)
    #             if not regno or line_upper != regno:
    #                 # Clean the line for name detection
    #                 clean_line = re.sub(r'[^A-Z\s]', '', line_upper).strip()
    #                 if len(clean_line) > 5 and not name:  # Names are usually longer than 5 chars
    #                     # Check if it looks like a name
    #                     words = clean_line.split()
    #                     if len(words) >= 2 and all(len(word) > 1 for word in words):
    #                         if validate_name(clean_line):
    #                             name = clean_line
    #                             log_message(f"Found name: {name}")
    #         
    #         return name, regno
    #         
    #     except Exception as e:
    #         log_message(f"Error in text pattern extraction: {str(e)}", "ERROR")
    #         return None, None
    
    def process_entire_frame(self, frame):
        """Process entire frame when card detection fails"""
        if self.processing:
            return
        
        self.processing = True
        self.update_status("Processing entire frame...")
        
        try:
            # Use a portion of the frame that likely contains the card
            height, width = frame.shape[:2]
            
            # Take center portion of frame (assuming card is roughly centered)
            center_x, center_y = width // 2, height // 2
            card_width, card_height = min(width // 2, 400), min(height // 2, 250)
            
            x1 = max(0, center_x - card_width // 2)
            x2 = min(width, center_x + card_width // 2)
            y1 = max(0, center_y - card_height // 2)
            y2 = min(height, center_y + card_height // 2)
            
            card_image = frame[y1:y2, x1:x2]
            
            if config.DEBUG_MODE:
                # Show the region being processed
                debug_frame = frame.copy()
                cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(debug_frame, "PROCESSING THIS REGION", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Processing Region", debug_frame)
                cv2.waitKey(1)
            
            # Extract text using OCR
            name, regno, confidences = self.ocr.extract_text_from_card(card_image)
            
            # Check if extraction was successful
            if self.ocr.is_text_extraction_successful(name, regno, confidences):
                # Mark attendance
                if self.sheets.mark_attendance(name, regno):
                    self.last_scan_time = time.time()
                    self.update_status(f"Attendance marked: {name}")
                    self.last_scan_label.config(text=f"Last Scan: {name} ({regno})")
                    self.update_attendance_count()
                    
                    # Show success message
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success", 
                        f"Attendance marked successfully!\n\nName: {name}\nRegNo: {regno}\nTime: {get_current_timestamp()}"
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", 
                        "Failed to mark attendance in Google Sheets"
                    ))
            else:
                # Try fallback extraction on entire frame
                name, regno, _ = self.ocr.extract_text_fallback(frame)
                
                if name and regno:
                    # Ask user for confirmation with fallback results
                    self.root.after(0, lambda: self.confirm_fallback_extraction(name, regno))
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Warning", 
                        "Could not extract clear text from frame. Please ensure the ID card is clearly visible and try again."
                    ))
        
        except Exception as e:
            log_message(f"Error processing entire frame: {str(e)}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error processing frame: {str(e)}"
            ))
        
        finally:
            self.processing = False
            self.update_status("Ready for next scan")

    def process_card(self, frame, card_contour):
        """Process detected ID card"""
        if self.processing:
            return
        
        self.processing = True
        self.update_status("Processing card...")
        
        try:
            # Extract card region
            card_image = self.camera.extract_card_region(frame, card_contour)
            
            if config.DEBUG_MODE:
                # Show regions on card for debugging
                debug_card = card_image.copy()
                debug_card = draw_text_regions(debug_card, config.NAME_REGION, config.REGNO_REGION)
                cv2.imshow("Debug - Card Regions", debug_card)
                cv2.waitKey(1)
            
            # Extract text using OCR
            name, regno, confidences = self.ocr.extract_text_from_card(card_image)
            
            # Check if extraction was successful
            if self.ocr.is_text_extraction_successful(name, regno, confidences):
                # Mark attendance
                if self.sheets.mark_attendance(name, regno):
                    self.last_scan_time = time.time()
                    self.update_status(f"Attendance marked: {name}")
                    self.last_scan_label.config(text=f"Last Scan: {name} ({regno})")
                    self.update_attendance_count()
                    
                    # Show success message
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Success", 
                        f"Attendance marked successfully!\n\nName: {name}\nRegNo: {regno}\nTime: {get_current_timestamp()}"
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", 
                        "Failed to mark attendance in Google Sheets"
                    ))
            else:
                # Try fallback extraction
                name, regno, _ = self.ocr.extract_text_fallback(card_image)
                
                if name and regno:
                    # Ask user for confirmation with fallback results
                    self.root.after(0, lambda: self.confirm_fallback_extraction(name, regno))
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Warning", 
                        "Could not extract clear text from ID card. Please try again with better lighting."
                    ))
        
        except Exception as e:
            log_message(f"Error processing card: {str(e)}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error processing card: {str(e)}"
            ))
        
        finally:
            self.processing = False
            self.update_status("Ready for next scan")
    
    def confirm_fallback_extraction(self, name, regno):
        """Confirm fallback extraction results with user"""
        result = messagebox.askyesno(
            "Confirm Extraction",
            f"OCR results (low confidence):\n\nName: {name}\nRegNo: {regno}\n\nMark attendance with these details?"
        )
        
        if result:
            if self.sheets.mark_attendance(name, regno):
                self.last_scan_time = time.time()
                self.update_status(f"Attendance marked: {name}")
                self.last_scan_label.config(text=f"Last Scan: {name} ({regno})")
                self.update_attendance_count()
                messagebox.showinfo("Success", "Attendance marked successfully!")
            else:
                messagebox.showerror("Error", "Failed to mark attendance in Google Sheets")
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=f"Status: {message}")
        log_message(message)
    
    def update_attendance_count(self):
        """Update today's attendance count"""
        try:
            stats = self.sheets.get_attendance_stats()
            self.attendance_count_label.config(text=f"Today's Attendance: {stats['count']}")
        except Exception as e:
            log_message(f"Error updating attendance count: {str(e)}", "WARNING")
    
    def open_google_sheet(self):
        """Open Google Sheet in web browser"""
        import webbrowser
        url = self.sheets.get_spreadsheet_url()
        webbrowser.open(url)
        log_message(f"Opened Google Sheet: {url}")
    
    def on_closing(self):
        """Handle application closing"""
        self.is_running = False
        time.sleep(0.1)  # Give time for threads to stop
        
        # Release camera
        self.camera.release_camera()
        
        # Close any OpenCV windows
        cv2.destroyAllWindows()
        
        log_message("Application closed")
        self.root.destroy()

def main():
    """Main function to run the application"""
    # Create the main window
    root = tk.Tk()
    
    # Create and run the application
    app = AttendanceApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI main loop
    root.mainloop()

if __name__ == "__main__":
    main()
