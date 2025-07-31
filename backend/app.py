from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import sys
from pathlib import Path
from werkzeug.utils import secure_filename

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.pdf_processor import PDFProcessor
from backend.llm_extractor import LLMExtractor
from config.settings import Config

app = Flask(__name__)
CORS(app)

# 配置
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE

# 初始化处理器
pdf_processor = PDFProcessor()
llm_extractor = LLMExtractor()

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传PDF文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 解析PDF
            pages_data = pdf_processor.extract_text_with_positions(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'pages': len(pages_data),
                'message': 'PDF上传并解析成功'
            })
        else:
            return jsonify({'error': '不支持的文件类型，请上传PDF文件'}), 400
            
    except Exception as e:
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/api/extract', methods=['POST'])
def extract_information():
    """从PDF中抽取指定类型的信息"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        query_types = data.get('query_types', [])
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 400
        
        if not query_types:
            return jsonify({'error': '请指定查询类型'}), 400
        
        # 解析PDF获取文本和位置信息
        pages_data = pdf_processor.extract_text_with_positions(filepath)
        
        # 使用LLM抽取信息
        extracted_info = llm_extractor.extract_information(pages_data, query_types)
        
        return jsonify({
            'success': True,
            'extracted_info': extracted_info,
            'total_items': len(extracted_info)
        })
        
    except Exception as e:
        return jsonify({'error': f'信息抽取失败: {str(e)}'}), 500

@app.route('/api/query_types', methods=['GET'])
def get_query_types():
    """获取支持的查询类型"""
    query_types = [
        {'id': 'stock_name', 'name': '证券简称', 'description': '股票、基金等证券的简称'},
        {'id': 'company_name', 'name': '公司全称', 'description': '公司的完整名称'},
        {'id': 'person_name', 'name': '人名', 'description': '人员姓名'},
        {'id': 'numbers', 'name': '数字', 'description': '金额、百分比、代码等数字信息'},
        {'id': 'book_title', 'name': '书名号内容', 'description': '《》内的文字内容'},
        {'id': 'proposal', 'name': '提案/议案名', 'description': '提案或议案的名称'}
    ]
    return jsonify({'query_types': query_types})

@app.route('/api/pdf/<filename>')
def serve_pdf(filename):
    """提供PDF文件访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'message': 'AI Link系统运行正常'})

if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5001)