# OCR Web Application

A web application built with FastHTML that performs OCR (Optical Character Recognition) on uploaded images and PDFs using Google's Gemini API.

## Features

- Upload images (JPG, JPEG, PNG) or PDF files
- Extract text using Google Gemini AI
- Modern, responsive web interface
- Docker support for easy deployment

## Prerequisites

- Python 3.11+
- Docker (optional)

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t ocr-app .
```

2. Run the container:
```bash
docker run -p 5000:5000 ocr-app
```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Click "Choose File" and select an image or PDF
3. Click "Extract Text" to process the file
4. View the extracted text in the results area

## API Endpoints

- `GET /` - Main web interface
- `POST /ocr` - OCR processing endpoint (accepts file uploads)

## Dependencies

- **FastHTML**: Web framework
- **google-generativeai**: Google Gemini AI integration
- **Pillow**: Image processing
- **PyMuPDF**: PDF processing
- **python-multipart**: File upload handling

## Notes

- The application uses port 5000 as specified in the FastHTML documentation
- The Gemini API key is configured in the application
- The Dockerfile uses Debian base image with required system dependencies
