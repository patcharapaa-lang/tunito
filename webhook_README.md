# LINE Bot Webhook Server

A FastHTML-based webhook server that receives LINE Bot webhook events and automatically replies with predefined messages.

## Features

- Receives LINE Bot webhook POST requests at `/webhook`
- Automatically replies to user messages with "Hello, user" and "May I help you?"
- Uses FastHTML framework on port 5001 (default)
- Docker support for easy deployment

## Configuration

The webhook server is configured with:
- **Channel Access Token**: `Am/TUFGz2OjG0YjSQmmhQ99jORlQkR1s+w3tyFgDSGYcCCMB/uNpGbhENGDP852REpwmkSCrIZacH8x36zcrAplT2cmBaQrL2wpNOh7iWuGO8RU14JGyhvNOo0AB2WZHT3Z8lwWsMQtxGTi2mqFUQdB04t89/1O/w1cDnyilFU=`
- **LINE API Endpoint**: `https://api.line.me/v2/bot/message/reply`
- **Port**: 5001 (FastHTML default)

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r webhook_requirements.txt
```

2. Run the application:
```bash
python webhook_app.py
```

The webhook will be available at `http://localhost:5001/webhook`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -f webhook_Dockerfile -t line-webhook .
```

2. Run the container:
```bash
docker run -p 5001:5001 line-webhook
```

## Usage

1. Configure your LINE Bot webhook URL to point to your server:
   - For local testing: `http://your-domain:5001/webhook`
   - For production: `https://your-domain.com/webhook`

2. The webhook will automatically:
   - Receive POST requests from LINE
   - Extract the `replyToken` from message events
   - Send a reply with two messages:
     - "Hello, user"
     - "May I help you?"

## API Endpoints

- `GET /` - Status page showing webhook server information
- `POST /webhook` - LINE Bot webhook endpoint

## Files

- `webhook_app.py` - Main FastHTML application
- `webhook_requirements.txt` - Python dependencies
- `webhook_Dockerfile` - Docker configuration
- `webhook_README.md` - This documentation

## Notes

- The server uses FastHTML framework on port 5001
- All message events trigger the same reply
- Error handling is included for failed API calls
- The server logs successful and failed reply attempts
