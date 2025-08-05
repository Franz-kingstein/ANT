#!/usr/bin/env python3
"""
Smart Attendance System - Web Application
Flask-based web interface for Render deployment
"""

import os
import json
import cv2
import base64
import numpy as np
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime, date
import logging
from io import BytesIO
from PIL import Image
import threading
import time
import atexit
from mailer import send_attendance_report

# Import our existing modules
from qr_processor import QRProcessor
from sheets_manager import SheetsManager
from utils import validate_urk_number, extract_name_from_urk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart-attendance-system-2025')

# Global instances
qr_processor = QRProcessor()
sheets_manager = None

# Initialize Google Sheets if credentials are available
def init_sheets_manager():
    global sheets_manager
    try:
        # Check for credentials in environment variable (for Render)
        if os.environ.get('GOOGLE_CREDENTIALS_JSON'):
            credentials_data = json.loads(os.environ.get('GOOGLE_CREDENTIALS_JSON'))
            with open('credentials.json', 'w') as f:
                json.dump(credentials_data, f)
            sheets_manager = SheetsManager()
            logger.info("Google Sheets manager initialized from environment")
        elif os.path.exists('credentials.json'):
            sheets_manager = SheetsManager()
            logger.info("Google Sheets manager initialized from file")
        else:
            logger.warning("No Google Sheets credentials found")
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets: {e}")

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """Upload page for barcode scanning"""
    return render_template('upload.html')

@app.route('/attendance')
def attendance_page():
    """Attendance records page"""
    return render_template('attendance.html')

@app.route('/api/process_image', methods=['POST'])
def process_image():
    """Process uploaded image for barcode detection"""
    try:
        # Get image data from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read and process image
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Detect barcodes
        detections = qr_processor.detect_qr_codes(image)
        
        results = []
        for detection in detections:
            try:
                # Extract registration number
                barcode_data = detection.data.decode('utf-8')
                reg_number = qr_processor.extract_registration_number(barcode_data)
                
                if reg_number and validate_urk_number(reg_number):
                    student_name = extract_name_from_urk(reg_number)
                    
                    result = {
                        'type': detection.type.name,
                        'data': barcode_data,
                        'reg_number': reg_number,
                        'student_name': student_name,
                        'valid': True
                    }
                    
                    # Mark attendance if sheets manager is available
                    if sheets_manager:
                        success, message = sheets_manager.mark_attendance(reg_number, student_name)
                        result['attendance_marked'] = success
                        result['message'] = message
                    else:
                        result['attendance_marked'] = False
                        result['message'] = 'Google Sheets not configured'
                    
                    results.append(result)
                else:
                    results.append({
                        'type': detection.type.name,
                        'data': barcode_data,
                        'reg_number': None,
                        'student_name': None,
                        'valid': False,
                        'message': 'Invalid registration number format'
                    })
            except Exception as e:
                logger.error(f"Error processing detection: {e}")
                continue
        
        if not results:
            return jsonify({
                'success': False,
                'message': 'No valid barcodes found in image',
                'results': []
            })
        
        return jsonify({
            'success': True,
            'message': f'Found {len(results)} valid barcode(s)',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process_camera', methods=['POST'])
def process_camera():
    """Process image from camera (base64 encoded)"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Process image (same logic as process_image)
        detections = qr_processor.detect_qr_codes(image)
        
        results = []
        for detection in detections:
            try:
                barcode_data = detection.data.decode('utf-8')
                reg_number = qr_processor.extract_registration_number(barcode_data)
                
                if reg_number and validate_urk_number(reg_number):
                    student_name = extract_name_from_urk(reg_number)
                    
                    result = {
                        'type': detection.type.name,
                        'data': barcode_data,
                        'reg_number': reg_number,
                        'student_name': student_name,
                        'valid': True
                    }
                    
                    if sheets_manager:
                        success, message = sheets_manager.mark_attendance(reg_number, student_name)
                        result['attendance_marked'] = success
                        result['message'] = message
                    else:
                        result['attendance_marked'] = False
                        result['message'] = 'Google Sheets not configured'
                    
                    results.append(result)
            except Exception as e:
                logger.error(f"Error processing detection: {e}")
                continue
        
        return jsonify({
            'success': len(results) > 0,
            'message': f'Found {len(results)} valid barcode(s)' if results else 'No valid barcodes found',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing camera image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/today')
def get_today_attendance():
    """Get today's attendance records"""
    try:
        if not sheets_manager:
            return jsonify({'error': 'Google Sheets not configured'}), 500
        
        today = date.today().strftime("%Y-%m-%d")
        records = sheets_manager.get_attendance_summary(today)
        
        return jsonify({
            'success': True,
            'date': today,
            'total': len(records),
            'records': records
        })
        
    except Exception as e:
        logger.error(f"Error getting attendance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/<date_str>')
def get_attendance_by_date(date_str):
    """Get attendance records for specific date"""
    try:
        if not sheets_manager:
            return jsonify({'error': 'Google Sheets not configured'}), 500
        
        records = sheets_manager.get_attendance_summary(date_str)
        
        return jsonify({
            'success': True,
            'date': date_str,
            'total': len(records),
            'records': records
        })
        
    except Exception as e:
        logger.error(f"Error getting attendance for {date_str}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test_connection')
def test_connection():
    """Test Google Sheets connection"""
    try:
        if not sheets_manager:
            return jsonify({
                'success': False,
                'message': 'Google Sheets not configured'
            })
        
        success = sheets_manager.test_connection()
        return jsonify({
            'success': success,
            'message': 'Connection successful' if success else 'Connection failed'
        })
        
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'sheets_configured': sheets_manager is not None,
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize sheets manager and create a new attendance sheet
    init_sheets_manager()
    # Prompt for email address to send the report on exit
    user_email = None
    try:
        user_email = input("Enter your email address to receive the attendance report on exit: ").strip()
    except Exception:
        pass
    # Register exit hook to email the attendance report
    if sheets_manager and user_email:
        atexit.register(lambda: send_attendance_report(sheets_manager.get_attendance(), user_email))
    # Get port from environment (for Render)
    port = int(os.environ.get('PORT', 5000))
    # Run app
    app.run(host='0.0.0.0', port=port, debug=False)
