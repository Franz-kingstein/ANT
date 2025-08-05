#!/usr/bin/env python3
"""
PDF Generator for Smart Attendance System Documentation
Converts the comprehensive Markdown guide into a professional PDF
"""

import os
import sys
import markdown
import weasyprint
from weasyprint import HTML, CSS
from markdown.extensions import codehilite, tables, toc
import base64
from datetime import datetime

def create_pdf_styles():
    """Create CSS styles for professional PDF formatting"""
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "Smart Attendance System - Developer Guide";
            font-family: Arial, sans-serif;
            font-size: 10pt;
            color: #666;
        }
        @bottom-center {
            content: "Page " counter(page);
            font-family: Arial, sans-serif;
            font-size: 10pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        color: #333;
        margin: 0;
        padding: 0;
    }
    
    /* Typography */
    h1 {
        color: #2c3e50;
        font-size: 2.5em;
        margin-top: 30px;
        margin-bottom: 20px;
        page-break-before: always;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    
    h1:first-child {
        page-break-before: avoid;
        text-align: center;
        color: #e74c3c;
        font-size: 3em;
        margin-top: 0;
    }
    
    h2 {
        color: #34495e;
        font-size: 1.8em;
        margin-top: 25px;
        margin-bottom: 15px;
        border-left: 4px solid #3498db;
        padding-left: 15px;
    }
    
    h3 {
        color: #2c3e50;
        font-size: 1.4em;
        margin-top: 20px;
        margin-bottom: 12px;
    }
    
    h4 {
        color: #34495e;
        font-size: 1.2em;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    p {
        margin-bottom: 12px;
        text-align: justify;
    }
    
    /* Code blocks */
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 15px;
        margin: 15px 0;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        line-height: 1.4;
    }
    
    code {
        background-color: #f1f3f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        color: #d73a49;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
        color: #333;
    }
    
    /* Lists */
    ul, ol {
        margin-bottom: 15px;
        padding-left: 25px;
    }
    
    li {
        margin-bottom: 8px;
    }
    
    /* Tables */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.9em;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    
    th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    /* Blockquotes */
    blockquote {
        border-left: 4px solid #3498db;
        margin: 15px 0;
        padding: 10px 20px;
        background-color: #f8f9fa;
        font-style: italic;
    }
    
    /* Links */
    a {
        color: #3498db;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Special sections */
    .emoji-section {
        background-color: #e8f4fd;
        border: 1px solid #3498db;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
    
    /* Feature boxes */
    .feature-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 6px;
        padding: 12px;
        margin: 10px 0;
    }
    
    /* Warning boxes */
    .warning-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 6px;
        padding: 12px;
        margin: 10px 0;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 6px;
        padding: 12px;
        margin: 10px 0;
    }
    
    /* Page breaks */
    .page-break {
        page-break-before: always;
    }
    
    /* Architecture diagrams */
    .architecture-diagram {
        text-align: center;
        font-family: monospace;
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        padding: 20px;
        margin: 20px 0;
        white-space: pre;
        font-size: 0.8em;
    }
    
    /* File structure */
    .file-structure {
        font-family: monospace;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 15px;
        margin: 15px 0;
        white-space: pre;
        font-size: 0.9em;
    }
    
    /* Status indicators */
    .status-success::before {
        content: "✅ ";
        color: #28a745;
    }
    
    .status-error::before {
        content: "❌ ";
        color: #dc3545;
    }
    
    .status-warning::before {
        content: "⚠️ ";
        color: #ffc107;
    }
    
    .status-info::before {
        content: "ℹ️ ";
        color: #17a2b8;
    }
    
    /* Metrics table */
    .metrics-table {
        background-color: #f8f9fa;
    }
    
    .metrics-table th {
        background-color: #6c757d;
    }
    
    /* TOC styling */
    .toc {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 20px;
        margin: 20px 0;
        border-radius: 6px;
    }
    
    .toc ul {
        list-style-type: none;
        padding-left: 20px;
    }
    
    .toc > ul {
        padding-left: 0;
    }
    
    .toc a {
        text-decoration: none;
        color: #495057;
    }
    
    .toc a:hover {
        color: #3498db;
        text-decoration: underline;
    }
    
    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 30px;
        background-color: #f8f9fa;
        text-align: center;
        font-size: 0.8em;
        color: #666;
        line-height: 30px;
    }
    """
    
    return CSS(string=css_content)

def enhance_markdown_content(content):
    """Enhance markdown content with additional styling and structure"""
    
    # Add title page
    title_page = f"""
# 📋 Smart Attendance System
## Complete Developer Guide

### 🎓 Karunya Institute of Technology and Sciences

---

**Project Type:** Computer Vision & Automation System  
**Technology Stack:** Python, OpenCV, Google Sheets API  
**Target Audience:** Developers, System Administrators  
**Documentation Version:** 1.0  
**Generated:** {datetime.now().strftime("%B %d, %Y")}  

---

### 📖 About This Guide

This comprehensive guide provides everything needed to understand, build, deploy, and maintain the Smart Attendance System. Whether you're a beginner or experienced developer, this guide will walk you through every aspect of the project.

### 🎯 What You'll Learn

- Complete system architecture and design patterns
- Step-by-step implementation of computer vision components
- Google Sheets API integration and authentication
- Production deployment and monitoring strategies
- Advanced features and future enhancements
- Troubleshooting and optimization techniques

---

<div class="page-break"></div>

## 📑 Table of Contents

"""
    
    # Process content to add special styling
    enhanced_content = title_page + content
    
    # Add styling classes to certain sections
    enhancements = [
        # Feature lists
        (r'✅ \*\*(.*?)\*\*', r'<span class="status-success">**\1**</span>'),
        (r'❌ \*\*(.*?)\*\*', r'<span class="status-error">**\1**</span>'),
        (r'⚠️ \*\*(.*?)\*\*', r'<span class="status-warning">**\1**</span>'),
        (r'ℹ️ \*\*(.*?)\*\*', r'<span class="status-info">**\1**</span>'),
        
        # Architecture diagrams
        (r'```\n(┌─.*?\n.*?└─.*?)\n```', r'<div class="architecture-diagram">\1</div>'),
        
        # File structures  
        (r'```\n([a-zA-Z_]+/\n├──.*?)\n```', r'<div class="file-structure">\1</div>'),
    ]
    
    import re
    for pattern, replacement in enhancements:
        enhanced_content = re.sub(pattern, replacement, enhanced_content, flags=re.DOTALL)
    
    return enhanced_content

def markdown_to_html(markdown_content):
    """Convert markdown to HTML with extensions"""
    
    # Configure markdown extensions
    extensions = [
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.fenced_code',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.footnotes',
        'markdown.extensions.meta',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
        'markdown.extensions.wikilinks'
    ]
    
    extension_configs = {
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': True,
            'pygments_style': 'colorful'
        },
        'toc': {
            'anchorlink': True,
            'permalink': True,
            'baselevel': 1,
            'toc_depth': 3
        }
    }
    
    # Create markdown instance
    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=extension_configs,
        output_format='html5'
    )
    
    # Convert to HTML
    html_content = md.convert(markdown_content)
    
    # Get CSS content
    css_styles = create_pdf_styles()
    
    # Create complete HTML document
    html_document = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Attendance System - Developer Guide</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return html_document

def generate_pdf(input_file, output_file):
    """Generate PDF from markdown file"""
    
    try:
        print(f"📖 Reading markdown file: {input_file}")
        
        # Read markdown content
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print("🔧 Enhancing markdown content...")
        
        # Enhance content
        enhanced_content = enhance_markdown_content(markdown_content)
        
        print("🔄 Converting markdown to HTML...")
        
        # Convert to HTML
        html_content = markdown_to_html(enhanced_content)
        
        print("🎨 Applying styles and formatting...")
        
        # Create CSS styles
        css_styles = create_pdf_styles()
        
        print("📄 Generating PDF...")
        
        # Generate PDF
        html_doc = HTML(string=html_content)
        html_doc.write_pdf(
            output_file,
            stylesheets=[css_styles],
            optimize_images=True,
            jpeg_quality=95,
            pdf_version='1.7'
        )
        
        print(f"✅ PDF generated successfully: {output_file}")
        
        # Get file size
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📊 File size: {file_size_mb:.2f} MB")
        print(f"📄 Total pages: {get_pdf_page_count(output_file)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        return False

def get_pdf_page_count(pdf_file):
    """Get the number of pages in PDF"""
    try:
        import PyPDF2
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            return len(pdf_reader.pages)
    except:
        return "Unknown"

def create_enhanced_documentation():
    """Create additional documentation files"""
    
    # Create quick reference guide
    quick_ref_content = """
# Quick Reference Guide

## 🚀 Quick Start Commands

```bash
# Setup
git clone https://github.com/Franz-kingstein/ANT.git
cd ANT
python3 -m venv attendance_env
source attendance_env/bin/activate
pip install -r requirements.txt

# Run
python main.py
```

## 🔧 Common Commands

```bash
# Test camera
python -c "import cv2; print('Camera OK' if cv2.VideoCapture(0).isOpened() else 'Failed')"

# Test barcode detection
python test_qr.py

# Check Google Sheets connection
python check_sheets.py
```

## 📋 Troubleshooting Checklist

- [ ] Camera permissions granted
- [ ] credentials.json file present
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Google Sheets shared with service account
- [ ] Proper lighting for barcode scanning

## 🔗 Important Links

- Repository: https://github.com/Franz-kingstein/ANT
- Google Sheets API: https://developers.google.com/sheets/api
- OpenCV Documentation: https://docs.opencv.org/
"""
    
    with open('QUICK_REFERENCE.md', 'w') as f:
        f.write(quick_ref_content)
    
    print("📝 Created QUICK_REFERENCE.md")

def main():
    """Main function to generate comprehensive PDF documentation"""
    
    print("🎯 Smart Attendance System - PDF Documentation Generator")
    print("=" * 60)
    
    # Check if input file exists
    input_file = "COMPLETE_PROJECT_GUIDE.md"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Smart_Attendance_System_Guide_{timestamp}.pdf"
    
    print(f"📄 Input:  {input_file}")
    print(f"📄 Output: {output_file}")
    print()
    
    # Install required packages if missing
    try:
        import weasyprint
        import markdown
    except ImportError as e:
        print("❌ Missing required packages. Installing...")
        os.system("pip install weasyprint markdown pygments")
        print("✅ Packages installed. Please run the script again.")
        return False
    
    # Generate PDF
    success = generate_pdf(input_file, output_file)
    
    if success:
        print()
        print("🎉 Documentation Generation Complete!")
        print("=" * 40)
        print(f"📖 Comprehensive Guide: {output_file}")
        
        # Create additional documentation
        create_enhanced_documentation()
        
        print()
        print("📚 Additional Resources Created:")
        print("  - QUICK_REFERENCE.md")
        print()
        print("🚀 Ready for distribution and learning!")
        
        return True
    else:
        print("❌ Failed to generate PDF documentation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
