from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import io
import base64  # ✅ Added for Base64 decoding
from pdfminer.high_level import extract_text
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

        # ---------------------------------------------------------
        # OPTION A: Handle Base64 Data (The "Free Firestore Hack")
        # ---------------------------------------------------------
        if 'file_data' in data:
            b64_string = data['file_data']
            
            # Clean the string if it has the "data:application/pdf;base64," prefix
            if "," in b64_string:
                b64_string = b64_string.split(",")[1]
            
            # Decode the string back into bytes
            pdf_bytes = base64.b64decode(b64_string)
            pdf_file = io.BytesIO(pdf_bytes)

        # ---------------------------------------------------------
        # OPTION B: Handle URL (The original Firebase Storage way)
        # ---------------------------------------------------------
        elif 'url' in data:
            file_url = data['url']
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()
            pdf_file = io.BytesIO(response.content)

        else:
            return jsonify({"success": False, "error": "No 'file_data' or 'url' provided"}), 400

        # ---------------------------------------------------------
        # EXTRACT TEXT
        # ---------------------------------------------------------
        if pdf_file:
            raw_text = extract_text(pdf_file)
            return jsonify({
                "success": True, 
                "text": raw_text
            })
        else:
            return jsonify({"success": False, "error": "Failed to process file"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000)) 
    app.run(host='0.0.0.0', port=port)