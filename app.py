from fasthtml import *
import google.generativeai as genai
import os
import tempfile
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import io
import base64

# Configure Gemini API
genai.configure(api_key="AIzaSyD4P8-6gLsW4qDdl3JV2gIIedH9GOMfV4k")

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Create the FastHTML app
app = FastHTML()

@app.get("/")
def home():
    return html(
        head(
            title("OCR Web Application"),
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css")
        ),
        body(
            div(
                div(
                    h1("OCR Web Application", class_="text-3xl font-bold text-center mb-8 text-gray-800"),
                    div(
                        form(
                            div(
                                label("Upload Image or PDF:", class_="block text-sm font-medium text-gray-700 mb-2"),
                                input(type="file", id="fileInput", accept=".jpg,.jpeg,.png,.pdf", 
                                     class_="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"),
                                class_="mb-4"
                            ),
                            div(
                                button("Extract Text", type="submit", 
                                      class_="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"),
                                class_="mb-4"
                            )
                        ),
                        class_="bg-white p-6 rounded-lg shadow-md"
                    ),
                    div(
                        h2("Extracted Text:", class_="text-xl font-semibold mb-4 text-gray-800"),
                        div(id="result", class_="bg-gray-100 p-4 rounded-lg min-h-32 border-2 border-dashed border-gray-300"),
                        class_="mt-6"
                    ),
                    class_="max-w-2xl mx-auto p-6"
                ),
                class_="min-h-screen bg-gray-100 py-8"
            ),
            script("""
                document.querySelector('form').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const fileInput = document.getElementById('fileInput');
                    const resultDiv = document.getElementById('result');
                    
                    if (!fileInput.files[0]) {
                        alert('Please select a file');
                        return;
                    }
                    
                    resultDiv.innerHTML = '<div class="text-center"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div><p class="mt-2">Processing...</p></div>';
                    
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    
                    try {
                        const response = await fetch('/ocr', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            resultDiv.innerHTML = `<div class="bg-green-50 border border-green-200 rounded-lg p-4"><h3 class="font-semibold text-green-800 mb-2">Extracted Text:</h3><pre class="whitespace-pre-wrap text-gray-700">${data.text}</pre></div>`;
                        } else {
                            resultDiv.innerHTML = `<div class="bg-red-50 border border-red-200 rounded-lg p-4"><p class="text-red-800">Error: ${data.error}</p></div>`;
                        }
                    } catch (error) {
                        resultDiv.innerHTML = `<div class="bg-red-50 border border-red-200 rounded-lg p-4"><p class="text-red-800">Error: ${error.message}</p></div>`;
                    }
                });
            """)
        )
    )

@app.post("/ocr")
def process_ocr(file: UploadFile):
    try:
        # Read the uploaded file
        file_content = file.file.read()
        
        # Process based on file type
        if file.filename.lower().endswith('.pdf'):
            # Process PDF
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            images = []
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                images.append(img_data)
            
            pdf_document.close()
            
            # Process each page
            all_text = []
            for i, img_data in enumerate(images):
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_data))
                
                # Convert to base64 for Gemini API
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Send to Gemini for OCR
                response = model.generate_content([
                    "Extract all text from this image. Return only the text content, no additional formatting or explanations.",
                    {
                        "mime_type": "image/png",
                        "data": img_base64
                    }
                ])
                
                if response.text:
                    all_text.append(f"Page {i+1}:\n{response.text}\n")
            
            extracted_text = "\n".join(all_text)
            
        else:
            # Process image
            img = Image.open(io.BytesIO(file_content))
            
            # Convert to base64 for Gemini API
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Send to Gemini for OCR
            response = model.generate_content([
                "Extract all text from this image. Return only the text content, no additional formatting or explanations.",
                {
                    "mime_type": "image/png",
                    "data": img_base64
                }
            ])
            
            extracted_text = response.text if response.text else "No text found in the image."
        
        return {"success": True, "text": extracted_text}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Run on port 5000 as specified in FastHTML documentation
    app.run(port=5000, host="0.0.0.0")
