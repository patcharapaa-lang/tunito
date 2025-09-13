# Use Debian as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libfontconfig1 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libtiff6 \
    libopenjp2-7 \
    libwebp7 \
    libharfbuzz0b \
    libfribidi0 \
    libxft2 \
    libxss1 \
    libgcc-s1 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port 5001
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
