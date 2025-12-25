from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import io
from pdfminer.high_level import extract_text
import os

app = Flask(__name__)
CORS(app) # Allows your App to talk to this Server

@app.route('/', methods=['GET'])
def home():
    return "PDF Parser is Running!", 200

@app.route('/parse-pdf', methods=['POST'])
def parse_pdf():
    try:
        # 1. Get URL from App
        data = request.json
        file_url = data.get('url')

        if not file_url:
            return jsonify({"success": False, "error": "No URL provided"}), 400

        # 2. Download PDF
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()

        # 3. Extract Text
        with io.BytesIO(response.content) as pdf_file:
            raw_text = extract_text(pdf_file)

        # 4. Return Text
        return jsonify({
            "success": True, 
            "text": raw_text
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5000, debug=True)