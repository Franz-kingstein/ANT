# Dockerfile for Smart Attendance System

FROM python:3.12-slim

# Install system dependencies needed by zbar and OpenCV
RUN apt-get update && \
    apt-get install -y libzbar0 libzbar-dev libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose the server port
EXPOSE 5000

# Start the application with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
