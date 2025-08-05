# Smart Attendance System - Karunya Institute

🎯 **A Computer Vision-based Smart Attendance System for Karunya Institute**

This system uses computer vision to automatically mark attendance by scanning student ID cards with barcode/QR code detection.

## 🚀 Features

- **Multi-Barcode Support**: Detects QR codes, CODE128, and other barcode formats
- **Real-time Processing**: Live camera feed with instant barcode detection
- **Google Sheets Integration**: Automatic attendance logging to Google Sheets
- **URK Validation**: Validates Karunya Institute registration numbers (URK format)
- **Duplicate Prevention**: Prevents multiple attendance entries per day
- **High-Resolution Camera Support**: Works with Iriun Webcam and other cameras
- **Auto-correction**: Fixes common barcode reading errors
- **User-friendly GUI**: Simple Tkinter interface

## 📋 System Requirements

- Python 3.8+
- OpenCV 4.8+
- Google Cloud API credentials
- Camera (built-in, USB, or Iriun Webcam)

## 🛠 Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Franz-kingstein/ANT.git
   cd ANT
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv attendance_env
   source attendance_env/bin/activate  # Linux/Mac
   # or
   attendance_env\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Google Sheets API:**

   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Create service account credentials
   - Download `credentials.json` and place in project root
   - Share your Google Sheet with the service account email

5. **Configure the system:**
   - Update `SHEET_ID` in `config.py` with your Google Sheet ID
   - Adjust camera settings if needed

## 🎮 Usage

1. **Run the system:**

   ```bash
   python main.py
   ```

2. **Using the interface:**
   - Click "Start Camera" to begin
   - Hold your Karunya ID card in front of the camera
   - The system will automatically detect the barcode and mark attendance
   - Check your Google Sheet for attendance records

## 📁 Project Structure

```
attendance/
├── main.py              # Main application with GUI
├── qr_processor.py      # Barcode/QR code detection
├── camera_handler.py    # Camera management
├── sheets_manager.py    # Google Sheets integration
├── utils.py            # Utility functions
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── verify_setup.sh     # Setup verification script
└── README.md          # This file
```

## 🔧 Configuration

### Camera Settings (`config.py`)

- `CAMERA_INDEX`: Camera device index (0=built-in, 2=Iriun)
- `CAMERA_WIDTH/HEIGHT`: Resolution settings
- `FPS`: Frame rate

### Google Sheets (`config.py`)

- `SHEET_ID`: Your Google Sheet ID
- `SHEET_NAME`: Name of the sheet tab
- `CREDENTIALS_FILE`: Path to Google API credentials

## 🎯 Supported Barcode Formats

- QR Code
- CODE128
- CODE39
- DataMatrix
- And more via pyzbar library

## 🔐 Security

- Sensitive credentials are excluded from Git via `.gitignore`
- Service account authentication for Google Sheets API
- Local processing - no data sent to external servers

## 🚨 Troubleshooting

1. **Camera not detected**: Check `CAMERA_INDEX` in `config.py`
2. **Google Sheets error**: Verify credentials and sheet sharing
3. **Barcode not scanning**: Ensure good lighting and steady card positioning

## 👨‍💻 Developer

**Franz Kingstein**

- GitHub: [@Franz-kingstein](https://github.com/Franz-kingstein)
- Project: Smart Attendance System for Karunya Institute

## 📄 License

This project is developed for educational purposes at Karunya Institute.

## 🙏 Acknowledgments

- Karunya Institute of Technology and Sciences
- Google Sheets API
- OpenCV Community
- pyzbar library developers

---

**Made with ❤️ for Karunya Institute Students**

- **User-friendly Interface**: Simple GUI with camera preview

## System Requirements

- Python 3.8+
- Webcam
- Internet connection for Google Sheets API

## Installation

1. Install required packages:

```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows - Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

3. Set up Google Sheets API:
   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Create service account and download credentials
   - Share your Google Sheet with service account email

## Usage

1. Place your `credentials.json` file in the project directory
2. Update the `SHEET_ID` in `config.py` with your Google Sheet ID
3. Run the application:

```bash
python main.py
```

## Project Structure

```
attendance/
├── main.py              # Main application entry point
├── camera_handler.py    # Camera and video processing
├── ocr_processor.py     # OCR and text extraction
├── sheets_manager.py    # Google Sheets integration
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── utils.py           # Utility functions
└── README.md          # Project documentation
```

## How it works

1. **Camera Capture**: Continuously captures frames from webcam
2. **Card Detection**: Detects rectangular objects (ID cards) in the frame
3. **Region Extraction**: Identifies name (red box area) and regno (green box area)
4. **OCR Processing**: Uses Tesseract to extract text from these regions
5. **Data Validation**: Validates extracted data format
6. **Attendance Logging**: Records attendance in Google Sheets with timestamp

## Configuration

Edit `config.py` to customize:

- Camera settings
- OCR parameters
- Google Sheets configuration
- UI settings
