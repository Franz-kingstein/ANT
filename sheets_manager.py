"""
Google Sheets Manager for Smart Attendance System
Handles Google Sheets API integration for attendance logging
"""

import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils import log_message, get_current_timestamp, get_current_date
import config

class SheetsManager:
    def __init__(self):
        """
        Initialize SheetsManager with a dynamic sheet tab name based on timestamp.
        """
        from datetime import datetime
        self.service = None
        self.spreadsheet_id = config.SHEET_ID
        # Generate a unique sheet tab name with timestamp
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.sheet_name = f"{config.SHEET_NAME}_{ts}"
        self.credentials_file = config.CREDENTIALS_FILE
        
    def initialize_sheets_api(self):
        """Initialize Google Sheets API connection"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_file):
                log_message(f"Credentials file not found: {self.credentials_file}", "ERROR")
                return False
            
            # Set up credentials
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            
            # Test connection by trying to get spreadsheet metadata
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            log_message("Google Sheets API initialized successfully")
            log_message(f"Connected to spreadsheet: {sheet_metadata.get('properties', {}).get('title', 'Unknown')}")
            
            # Create the attendance sheet tab and set headers
            self._create_attendance_sheet()
            self._add_headers(['Date', 'Time', 'Name', 'Registration Number', 'Status'])
            
            return True
            
        except FileNotFoundError:
            log_message(f"Credentials file not found: {self.credentials_file}", "ERROR")
            return False
        except HttpError as e:
            log_message(f"Google Sheets API error: {str(e)}", "ERROR")
            return False
        except Exception as e:
            log_message(f"Failed to initialize Google Sheets API: {str(e)}", "ERROR")
            return False
    
    def _setup_attendance_sheet(self):
        """Setup attendance sheet with proper headers"""
        try:
            # Check if sheet exists
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_exists = False
            for sheet in sheet_metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == self.sheet_name:
                    sheet_exists = True
                    break
            
            # Create sheet if it doesn't exist
            if not sheet_exists:
                self._create_attendance_sheet()
            
            # Check if headers exist
            range_name = f"{self.sheet_name}!A1:E1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Add headers if they don't exist or are incomplete
            expected_headers = ['Date', 'Time', 'Name', 'Registration Number', 'Status']
            if not values or values[0] != expected_headers:
                self._add_headers(expected_headers)
                
        except Exception as e:
            log_message(f"Error setting up attendance sheet: {str(e)}", "ERROR")
    
    def _create_attendance_sheet(self):
        """Create a new attendance sheet"""
        try:
            request = {
                'addSheet': {
                    'properties': {
                        'title': self.sheet_name,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 5
                        }
                    }
                }
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
            log_message(f"Created new sheet: {self.sheet_name}")
            
        except Exception as e:
            log_message(f"Error creating sheet: {str(e)}", "ERROR")
    
    def _add_headers(self, headers):
        """Add headers to the attendance sheet"""
        try:
            range_name = f"{self.sheet_name}!A1:E1"
            
            body = {
                'values': [headers]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format headers (bold)
            self._format_headers()
            
            log_message("Added headers to attendance sheet")
            
        except Exception as e:
            log_message(f"Error adding headers: {str(e)}", "ERROR")
    
    def _format_headers(self):
        """Format header row (make bold, add background color)"""
        try:
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': self._get_sheet_id(),
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 5
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9,
                                    'blue': 0.9
                                },
                                'textFormat': {
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }
            ]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
        except Exception as e:
            log_message(f"Error formatting headers: {str(e)}", "WARNING")
    
    def _get_sheet_id(self):
        """Get the internal sheet ID for the attendance sheet"""
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            for sheet in sheet_metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == self.sheet_name:
                    return sheet.get('properties', {}).get('sheetId')
            
            return 0  # Fallback to first sheet
            
        except Exception:
            return 0
    
    def mark_attendance(self, name, regno):
        """
        Mark attendance for a student
        Returns True if successful, False otherwise
        """
        try:
            current_date = get_current_date()
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Check for duplicate entry if configured
            if config.PREVENT_DUPLICATE_DAILY:
                if self._check_duplicate_attendance(regno, current_date):
                    log_message(f"Duplicate attendance prevented for {regno} on {current_date}", "WARNING")
                    return False
            
            # Prepare the row data
            row_data = [
                current_date,
                current_time,
                name,
                regno,
                "Present"
            ]
            
            # Find the next empty row
            next_row = self._get_next_empty_row()
            range_name = f"{self.sheet_name}!A{next_row}:E{next_row}"
            
            # Insert the data
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            log_message(f"Attendance marked for {name} ({regno}) at {current_time}")
            return True
            
        except Exception as e:
            log_message(f"Error marking attendance: {str(e)}", "ERROR")
            return False
    
    def _check_duplicate_attendance(self, regno, date):
        """Check if attendance already exists for this student today"""
        try:
            # Get all data from the sheet
            range_name = f"{self.sheet_name}!A:E"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Skip header row and check for duplicates
            for row in values[1:]:
                if len(row) >= 4:  # Ensure row has enough columns
                    row_date = row[0] if len(row) > 0 else ""
                    row_regno = row[3] if len(row) > 3 else ""
                    
                    if row_date == date and row_regno == regno:
                        return True
            
            return False
            
        except Exception as e:
            log_message(f"Error checking duplicate attendance: {str(e)}", "WARNING")
            return False  # Allow attendance if check fails
    
    def _get_next_empty_row(self):
        """Find the next empty row in the sheet"""
        try:
            # Get all data to find the last row
            range_name = f"{self.sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return len(values) + 1
            
        except Exception as e:
            log_message(f"Error finding next empty row: {str(e)}", "WARNING")
            return 2  # Fallback to row 2 (after headers)
    
    def get_attendance_stats(self, date=None):
        """Get attendance statistics for a specific date or today"""
        try:
            if date is None:
                date = get_current_date()
            
            # Get all data from the sheet
            range_name = f"{self.sheet_name}!A:E"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Count attendance for the specified date
            count = 0
            students = []
            
            for row in values[1:]:  # Skip header
                if len(row) >= 4:
                    row_date = row[0] if len(row) > 0 else ""
                    if row_date == date:
                        count += 1
                        student_name = row[2] if len(row) > 2 else "Unknown"
                        students.append(student_name)
            
            return {
                'date': date,
                'count': count,
                'students': students
            }
            
        except Exception as e:
            log_message(f"Error getting attendance stats: {str(e)}", "ERROR")
            return {'date': date, 'count': 0, 'students': []}
    
    def get_spreadsheet_url(self):
        """Get the URL to access the Google Sheet"""
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
