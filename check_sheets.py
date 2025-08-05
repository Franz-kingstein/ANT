"""
Quick utility to check current attendance records in Google Sheets
"""

from sheets_manager import SheetsManager
from utils import get_current_date
import sys

def check_attendance_records():
    """Check current attendance records in Google Sheets"""
    try:
        print("🔍 Checking Google Sheets attendance records...")
        
        # Initialize sheets manager
        sheets = SheetsManager()
        
        # Ensure proper initialization
        if not sheets.service:
            print("⚠️  Initializing Google Sheets service...")
            sheets.initialize_sheets_api()
        
        # Get today's date
        today = get_current_date()
        print(f"📅 Today's date: {today}")
        
        # Try to read recent entries from the sheet directly
        try:
            sheet = sheets.service.spreadsheets()
            
            # Get the data range
            range_name = f"{sheets.sheet_name}!A:E"
            result = sheet.values().get(
                spreadsheetId=sheets.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if values:
                print(f"\n📋 Attendance Records in Google Sheets:")
                print("-" * 85)
                print(f"{'Date':<12} {'Time':<8} {'Name':<30} {'Reg No':<15} {'Status':<10}")
                print("-" * 85)
                
                # Count today's entries
                today_count = 0
                unique_students = set()
                
                # Show all entries (excluding header if it exists)
                data_rows = values[1:] if len(values) > 1 and 'Date' in str(values[0]) else values
                
                for entry in data_rows:
                    if len(entry) >= 4:  # Make sure we have enough columns
                        date = entry[0] if len(entry) > 0 else "N/A"
                        time = entry[1] if len(entry) > 1 else "N/A"
                        name = entry[2] if len(entry) > 2 else "N/A"
                        regno = entry[3] if len(entry) > 3 else "N/A"
                        status = entry[4] if len(entry) > 4 else "Present"
                        
                        print(f"{date:<12} {time:<8} {name:<30} {regno:<15} {status:<10}")
                        
                        # Count stats
                        if date == today:
                            today_count += 1
                        if regno != "N/A":
                            unique_students.add(regno)
                
                print("-" * 85)
                print(f"📊 Statistics:")
                print(f"   📅 Today's entries: {today_count}")
                print(f"   👥 Unique students: {len(unique_students)}")
                print(f"   📝 Total entries: {len(data_rows)}")
                
            else:
                print("\n⚠️  No entries found in the sheet")
                print("💡 This might be the first time running the system")
                
        except Exception as e:
            print(f"⚠️  Could not read sheet entries: {e}")
        
        print(f"\n✅ Google Sheets check complete!")
        print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{sheets.spreadsheet_id}")
        
    except Exception as e:
        print(f"❌ Error checking attendance records: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_attendance_records()
