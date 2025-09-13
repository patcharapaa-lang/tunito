from fasthtml import *
import requests
import json
import base64
import io
from PIL import Image
import google.generativeai as genai

# LINE Bot configuration
CHANNEL_ACCESS_TOKEN = "Am/TUFGz2OjG0YjSQmmhQ99jORlQkR1s+w3tyFgDSGYcCCMB/uNpGbhENGDP852REpwmkSCrIZacH8x36zcrAplT2cmBaQrL2wpNOh7iWuGO8RU14JGyhvNOo0AB2WZHT3Z8lwWsMQtxGTi2mqFUQdB04t89/1O/w1cDnyilFU="
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"
LINE_CONTENT_API_URL = "https://api-data.line.me/v2/bot/message"

# Configure Gemini API
genai.configure(api_key="AIzaSyD4P8-6gLsW4qDdl3JV2gIIedH9GOMfV4g")
model = genai.GenerativeModel('gemini-1.5-flash')

# Create the FastHTML app
app = FastHTML()

@app.get("/")
def home():
    return html(
        head(
            title("LINE Bot Webhook"),
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css")
        ),
        body(
            div(
                div(
                    h1("LINE Bot Webhook Server", class_="text-3xl font-bold text-center mb-8 text-gray-800"),
                    div(
                        p("Webhook endpoint is ready at:", class_="text-lg mb-2"),
                        code("/webhook", class_="bg-gray-100 px-3 py-1 rounded text-sm font-mono"),
                        class_="bg-white p-6 rounded-lg shadow-md text-center"
                    ),
                    div(
                        h2("Status:", class_="text-xl font-semibold mb-4 text-gray-800"),
                        div(
                            span("🟢 Online", class_="text-green-600 font-semibold"),
                            class_="bg-green-50 border border-green-200 rounded-lg p-4 text-center"
                        ),
                        class_="mt-6"
                    ),
                    class_="max-w-2xl mx-auto p-6"
                ),
                class_="min-h-screen bg-gray-100 py-8"
            )
        )
    )

@app.post("/webhook")
def webhook_handler(req):
    """Handle LINE webhook POST requests"""
    try:
        # Get the request body
        body = req.json()
        print(f"Received webhook payload: {json.dumps(body, indent=2)}")
        
        # Extract events from LINE webhook
        events = body.get('events', [])
        
        for event in events:
            # Check if it's a message event
            if event.get('type') == 'message':
                message = event.get('message', {})
                message_type = message.get('type')
                reply_token = event.get('replyToken')
                
                print(f"Extracted replyToken: {reply_token}")
                print(f"Event type: {event.get('type')}")
                print(f"Message type: {message_type}")
                
                if reply_token:
                    if message_type == 'image':
                        # Handle image message
                        message_id = message.get('id')
                        print(f"Processing image message with ID: {message_id}")
                        process_image_message(message_id, reply_token)
                    else:
                        # Handle text or other message types
                        print("Sending default reply for non-image message")
                        send_reply_message(reply_token)
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

def process_image_message(message_id, reply_token):
    """Process image message with OCR"""
    try:
        print(f"Starting image processing for message ID: {message_id}")
        
        # Get image content from LINE API
        image_data = get_image_content(message_id)
        if not image_data:
            print("Failed to get image content")
            send_reply_message(reply_token, ["Sorry, I couldn't process the image. Please try again."])
            return
        
        # Process image with Gemini OCR
        print("Processing image with Gemini OCR...")
        ocr_result = process_image_with_gemini(image_data)
        
        if ocr_result:
            print(f"OCR Result: {ocr_result}")
            send_reply_message(reply_token, [f"Here's the text I found in your image:\n\n{ocr_result}"])
        else:
            print("No text found in image")
            send_reply_message(reply_token, ["I couldn't find any text in this image. Please try with a clearer image."])
            
    except Exception as e:
        print(f"Error processing image message: {str(e)}")
        send_reply_message(reply_token, ["Sorry, there was an error processing your image. Please try again."])

def get_image_content(message_id):
    """Get image content from LINE API"""
    try:
        headers = {
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
        }
        
        url = f"{LINE_CONTENT_API_URL}/{message_id}/content"
        print(f"Requesting image content from: {url}")
        
        response = requests.get(url, headers=headers)
        print(f"Image content response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Successfully downloaded image content, size: {len(response.content)} bytes")
            return response.content
        else:
            print(f"Failed to get image content. Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting image content: {str(e)}")
        return None

def process_image_with_gemini(image_data):
    """Process image with Google Gemini for OCR"""
    try:
        # Convert image data to PIL Image
        image = Image.open(io.BytesIO(image_data))
        print(f"Image loaded successfully, size: {image.size}")
        
        # Convert to base64 for Gemini API
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        print("Sending image to Gemini for OCR processing...")
        
        # Send to Gemini for OCR
        response = model.generate_content([
            "Extract all text from this image. Return only the text content, no additional formatting or explanations.",
            {
                "mime_type": "image/png",
                "data": img_base64
            }
        ])
        
        if response.text:
            print(f"Gemini OCR completed successfully")
            return response.text.strip()
        else:
            print("No text extracted by Gemini")
            return None
            
    except Exception as e:
        print(f"Error processing image with Gemini: {str(e)}")
        return None

def send_reply_message(reply_token, messages=None):
    """Send reply message to LINE user"""
    try:
        if messages is None:
            messages = [
                "Hello, user",
                "May I help you?"
            ]
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
        }
        
        # Convert string messages to proper format
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "type": "text",
                "text": msg
            })
        
        data = {
            "replyToken": reply_token,
            "messages": formatted_messages
        }
        
        print(f"Sending reply with messages: {json.dumps(formatted_messages, indent=2)}")
        print(f"LINE API Request:")
        print(f"  URL: {LINE_API_URL}")
        print(f"  Headers: {headers}")
        print(f"  Payload: {json.dumps(data, indent=2)}")
        
        # Send POST request to LINE API
        response = requests.post(
            LINE_API_URL,
            headers=headers,
            data=json.dumps(data)
        )
        
        print(f"LINE API Response:")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Headers: {dict(response.headers)}")
        print(f"  Response Body: {response.text}")
        
        if response.status_code == 200:
            print(f"Reply sent successfully for token: {reply_token}")
        else:
            print(f"Failed to send reply. Status: {response.status_code}, Response: {response.text}")
            
    except Exception as e:
        print(f"Error sending reply message: {str(e)}")

if __name__ == "__main__":
    # Run on port 5001 (FastHTML default port)
    app.run(port=5001, host="0.0.0.0")
