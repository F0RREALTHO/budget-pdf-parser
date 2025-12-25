from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import io
import base64
from pypdf import PdfReader 
import os

app = Flask(__name__)
CORS(app) 

@app.route('/', methods=['GET'])
def home():
    return "PDF Parser is Running!", 200

@app.route('/parse-pdf', methods=['POST'])
def parse_pdf():
    try:
        data = request.json
        pdf_file = None

        if 'file_data' in data:
            b64_string = data['file_data']
            if "," in b64_string:
                b64_string = b64_string.split(",")[1]
            pdf_bytes = base64.b64decode(b64_string)
            pdf_file = io.BytesIO(pdf_bytes)
        elif 'url' in data:
            response = requests.get(data['url'])
            pdf_file = io.BytesIO(response.content)

        if pdf_file:
            reader = PdfReader(pdf_file)

            # ✅ FIX: Handle "Fake" Encryption
            if reader.is_encrypted:
                # 1. Try unlocking with an empty string first (Fixes files that allow reading but not editing)
                reader.decrypt("")
                
                # 2. If the user sent a specific password, try that logic
                if data.get('password'):
                    reader.decrypt(data.get('password'))

            # 3. Verify we can actually read the file
            try:
                # We try to access the first page. If it fails, it's truly locked.
                _ = len(reader.pages)
            except:
                # NOW we know it's actually locked
                return jsonify({"success": False, "error": "PASSWORD_REQUIRED"})

            # 4. Extract Text (Universal Layout Mode)
            text = ""
            for page in reader.pages:
                try:
                    page_text = page.extract_text(extraction_mode="layout")
                except:
                    page_text = page.extract_text()
                text += page_text + "\n"
            
            return jsonify({"success": True, "text": text})

        return jsonify({"success": False, "error": "No file provided"}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000)) 
    app.run(host='0.0.0.0', port=port)