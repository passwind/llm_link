from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import sys
from pathlib import Path
from werkzeug.utils import secure_filename

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.pdf_processor import PDFProcessor
from backend.llm_extractor import LLMExtractor
from config.settings import Config

# Create Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS support

# Configuration
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE

# Initialize components
pdf_processor = PDFProcessor()
llm_extractor = LLMExtractor()

# Allowed file types
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse PDF
            pages_data = pdf_processor.extract_text_with_positions(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'pages': len(pages_data),
                'message': 'PDF uploaded and parsed successfully'
            })
        else:
            return jsonify({'error': 'Unsupported file type, please upload PDF file'}), 400
            
    except Exception as e:
        return jsonify({'error': f'File upload failed: {str(e)}'}), 500

@app.route('/api/extract', methods=['POST'])
def extract_information():
    """Extract specified types of information from PDF"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        query_types = data.get('query_types', [])
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 400
        
        if not query_types:
            return jsonify({'error': 'Please specify query types'}), 400
        
        # Parse PDF to get text and position information
        pages_data = pdf_processor.extract_text_with_positions(filepath)
        
        # Use LLM to extract information
        extracted_info = llm_extractor.extract_information(pages_data, query_types)
        
        return jsonify({
            'success': True,
            'extracted_info': extracted_info,
            'total_items': len(extracted_info)
        })
        
    except Exception as e:
        return jsonify({'error': f'Information extraction failed: {str(e)}'}), 500

@app.route('/api/query_types', methods=['GET'])
def get_query_types():
    """Get supported query types"""
    query_types = [
        {'id': 'stock_name', 'name': 'Stock Name', 'description': 'Short names of stocks, funds and other securities'},
        {'id': 'company_name', 'name': 'Company Name', 'description': 'Full company names'},
        {'id': 'person_name', 'name': 'Person Name', 'description': 'Names of people'},
        {'id': 'numbers', 'name': 'Numbers', 'description': 'Amounts, percentages, codes and other numerical information'},
        {'id': 'book_title', 'name': 'Book Title', 'description': 'Text content within book title marks 《》'},
        {'id': 'proposal', 'name': 'Proposal/Motion', 'description': 'Names of proposals or motions'}
    ]
    return jsonify({'query_types': query_types})

@app.route('/api/pdf/<filename>')
def serve_pdf(filename):
    """Serve PDF file access"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({'status': 'healthy', 'message': 'AI Link system is running normally'})

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)