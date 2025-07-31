# Intelligent PDF Quick Link Query System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-green.svg)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent PDF document analysis and information extraction system powered by advanced Large Language Models (LLM). The system provides quick linkage query capabilities with precise positioning and context display.

[中文文档](README_CN.md) | [English](README.md)

## ✨ Key Features

### 🔍 Intelligent Information Extraction
- **Multi-type Query Support**: Stock names, company names, person names, numbers, book titles, proposal names
- **LLM-powered Analysis**: Leverages advanced AI models for accurate information understanding
- **Structured Output**: JSON-formatted results for easy processing and integration
- **Context Preservation**: Maintains original document context for each extracted item

### 📄 Advanced PDF Processing
- **Comprehensive Parsing**: Supports complex PDF documents with text and layout analysis
- **Precise Positioning**: Accurate location tracking for extracted information
- **Page-level Management**: Efficient handling of multi-page documents
- **Search and Navigation**: Quick content location and context retrieval

### 🤖 Multi-LLM Support
- **OpenAI GPT-4**: Industry-leading accuracy and performance
- **DeepSeek**: Excellent Chinese language support
- **Anthropic Claude**: Balanced performance and reliability
- **Local Models**: Complete offline operation for privacy protection

### 🌐 Interactive Web Interface
- **Intuitive Design**: User-friendly Streamlit-based interface
- **Drag-and-Drop Upload**: Easy file upload with progress tracking
- **Real-time Processing**: Live extraction progress and status updates
- **Linked Display**: Results linked to original document positions
- **Multi-language Support**: English and Chinese interface languages

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   LLM Services  │
│   (Streamlit)   │◄──►│    (Flask)      │◄──►│   (Multi-API)   │
│                 │    │                 │    │                 │
│ • File Upload   │    │ • PDF Parser    │    │ • OpenAI GPT-4  │
│ • Query Config  │    │ • LLM Extractor │    │ • DeepSeek      │
│ • Result View   │    │ • API Endpoints │    │ • Claude        │
│ • Multi-lang    │    │ • File Manager  │    │ • Local Models  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM (8GB+ recommended for local models)
- **Storage**: 2GB free space

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ai_link
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and settings
   ```

4. **Start the System**
   ```bash
   # Start both frontend and backend
   python start.py --all
   
   # Or start services separately
   python start.py --backend    # Backend only
   python start.py --frontend   # Frontend only
   ```

5. **Access the Application**
   - **Web Interface**: http://localhost:8501
   - **API Endpoint**: http://localhost:5001

## 📖 Usage Guide

### Basic Workflow

1. **Upload Document**: Drag and drop or select a PDF file
2. **Select Query Types**: Choose information types to extract
3. **Start Extraction**: Click "Extract Information" to begin processing
4. **View Results**: Browse extracted information with context
5. **Export Data**: Download results in JSON format

### Query Types

| Type | Description | Examples |
|------|-------------|----------|
| **Stock Names** | Securities and fund abbreviations | AAPL, TSLA, SPY |
| **Company Names** | Full corporate names | Apple Inc., Tesla Motors |
| **Person Names** | Individual names | John Smith, 张三 |
| **Numbers** | Amounts, percentages, codes | $1.2M, 15.5%, ID123 |
| **Book Titles** | Content within 《》 brackets | 《Data Science》 |
| **Proposals** | Proposal and motion names | Motion 2024-01 |

### Language Settings

The system supports both English and Chinese:

- **Default Language**: English
- **Language Switching**: Available in the sidebar
- **Auto-detection**: Based on document content
- **Fallback**: English for unsupported languages

## ⚙️ LLM Configuration

### OpenAI GPT-4
```bash
# .env configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1
```

### DeepSeek
```bash
# .env configuration
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### Anthropic Claude
```bash
# .env configuration
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229
```

### Local Models
```bash
# .env configuration
LOCAL_LLM_PATH=/path/to/your/model
LOCAL_LLM_MODEL=chatglm3-6b
```

## 🔌 API Reference

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file (required)

Response:
{
  "success": true,
  "filename": "document.pdf",
  "filepath": "/uploads/document.pdf",
  "pages": 10,
  "size": 1024000
}
```

### Extract Information
```http
POST /api/extract
Content-Type: application/json

{
  "filepath": "/uploads/document.pdf",
  "query_types": ["stock_name", "company_name"]
}

Response:
{
  "success": true,
  "extracted_info": [
    {
      "type": "stock_name",
      "value": "AAPL",
      "page": 1,
      "position": {"x": 100, "y": 200},
      "context": "Apple Inc. (AAPL) reported..."
    }
  ]
}
```

### Get Query Types
```http
GET /api/query_types

Response:
{
  "query_types": [
    {
      "name": "stock_name",
      "description": "Stock and security names",
      "examples": ["AAPL", "TSLA"]
    }
  ]
}
```

## 🛠️ Development Guide

### Project Structure

```
ai_link/
├── backend/                 # Backend Flask application
│   ├── app.py              # Main Flask app
│   ├── pdf_processor.py    # PDF processing logic
│   ├── llm_extractor.py    # LLM integration
│   └── local_llm.py        # Local model support
├── frontend/               # Frontend Streamlit app
│   └── streamlit_app.py    # Main Streamlit interface
├── config/                 # Configuration management
│   └── settings.py         # System settings
├── i18n/                   # Internationalization
│   ├── __init__.py         # I18n manager
│   └── locales/            # Language files
│       ├── en/messages.json # English translations
│       └── zh/messages.json # Chinese translations
├── tests/                  # Test suite
│   └── test_system.py      # System tests
├── uploads/                # File upload directory
├── models/                 # Model storage
└── static/                 # Static assets
```

### Adding New Query Types

1. **Update Language Files**: Add new type to `i18n/locales/*/messages.json`
2. **Modify Extractor**: Update `backend/llm_extractor.py` with new patterns
3. **Update Frontend**: Add new options to `frontend/streamlit_app.py`
4. **Test Integration**: Add tests to `tests/test_system.py`

### Custom LLM Integration

1. **Create Provider Class**: Extend base LLM interface
2. **Update Configuration**: Add new provider to `config/settings.py`
3. **Implement Extraction**: Add extraction logic to `llm_extractor.py`
4. **Test Functionality**: Verify with test documents

## 🧪 Testing

### Run System Tests
```bash
# Run all tests
python tests/test_system.py

# Run specific test
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=backend --cov=frontend
```

### Manual Testing
```bash
# Test with demo script
python demo.py

# Test API endpoints
curl -X GET http://localhost:5001/api/health
```

## 🔧 Troubleshooting

### Common Issues

**Backend Connection Failed**
- Check if backend service is running on port 5001
- Verify firewall settings and port availability
- Review backend logs for error messages

**File Upload Errors**
- Ensure file size is under 50MB limit
- Verify PDF file is not corrupted or password-protected
- Check available disk space in uploads directory

**LLM Extraction Failures**
- Verify API keys are correctly configured
- Check network connectivity to LLM services
- Review rate limits and quota usage
- Try alternative LLM providers

**Performance Issues**
- Increase system memory allocation
- Use smaller PDF files for testing
- Consider using cloud-based LLM services
- Optimize query types selection

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
python start.py --all

# Check logs
tail -f logs/app.log
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**: Submit your changes for review

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black backend/ frontend/ tests/
flake8 backend/ frontend/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyMuPDF & pdfplumber**: Excellent PDF processing libraries
- **Streamlit**: Amazing framework for rapid web app development
- **Flask**: Reliable and flexible web framework
- **OpenAI, Anthropic, DeepSeek**: Powerful LLM services
- **Open Source Community**: For continuous inspiration and support

## 📞 Contact

- **Project Repository**: [GitHub](https://github.com/your-username/ai_link)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-username/ai_link/issues)
- **Documentation**: [Wiki](https://github.com/your-username/ai_link/wiki)
- **Email**: your-email@example.com

---

**Built with ❤️ for intelligent document processing**