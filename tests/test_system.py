#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Function Test Script

Used to test core functions such as PDF processing and LLM extraction
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.pdf_processor import PDFProcessor
    from backend.llm_extractor import LLMExtractor
    from config.settings import Config
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

def test_config():
    """Test configuration"""
    print("🔧 Testing system configuration...")
    
    try:
        config = Config()
        print(f"✅ Upload directory: {config.UPLOAD_FOLDER}")
        print(f"✅ LLM provider: {config.LLM_PROVIDER}")
        
        # Check configuration validation
        errors = config.validate_config()
        if errors:
            print("⚠️  Configuration warnings:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ Configuration validation passed")
        
        # Get LLM configuration info
        llm_config = config.get_llm_config()
        print(f"✅ LLM configuration: {llm_config}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_pdf_processor():
    """Test PDF processor"""
    print("\n📄 Testing PDF processor...")
    
    try:
        processor = PDFProcessor()
        print("✅ PDF processor initialized successfully")
        
        # Test basic methods
        page_count = processor.get_page_count()
        print(f"✅ Page count method: {page_count}")
        
        return True
    except Exception as e:
        print(f"❌ PDF processor test failed: {str(e)}")
        return False

def test_llm_extractor():
    """Test LLM extractor"""
    print("\n🤖 Testing LLM extractor...")
    
    try:
        extractor = LLMExtractor()
        print("✅ LLM extractor initialized successfully")
        
        # Test rule extraction (not dependent on API)
        test_text = "本报告由《中国建设银行》提供，股票代码601939，涨幅15.5%。"
        
        # Simulate page data
        page_data = {
            'page_number': 1,
            'text_blocks': [
                {
                    'text': test_text,
                    'bbox': {'x0': 100, 'y0': 200, 'x1': 300, 'y1': 220}
                }
            ]
        }
        
        # Test book title extraction
        results = extractor._extract_with_rules(test_text, 'book_title', 1, page_data)
        print(f"✅ Book title extraction test: found {len(results)} results")
        
        # Test number extraction
        results = extractor._extract_with_rules(test_text, 'numbers', 1, page_data)
        print(f"✅ Number extraction test: found {len(results)} results")
        
        return True
    except Exception as e:
        print(f"❌ LLM extractor test failed: {str(e)}")
        return False

def test_local_llm():
    """Test local LLM (if available)"""
    print("\n🏠 Testing local LLM...")
    
    try:
        from backend.local_llm import LocalLLMManager
        
        manager = LocalLLMManager()
        print("✅ Local LLM manager initialized successfully")
        
        # Get model information
        model_info = manager.get_model_info()
        print(f"✅ Model information: {json.dumps(model_info, indent=2, ensure_ascii=False)}")
        
        # Check if local models are available
        model_path = model_info['model_path']
        if os.path.exists(model_path):
            print(f"✅ Model directory exists: {model_path}")
            
            # List available models
            models = [d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))]
            if models:
                print(f"✅ Available models: {models}")
            else:
                print("⚠️  Model directory is empty, please download models")
        else:
            print(f"⚠️  Model directory does not exist: {model_path}")
        
        return True
    except Exception as e:
        print(f"❌ Local LLM test failed: {str(e)}")
        return False

def create_sample_pdf():
    """Create sample PDF file for testing"""
    print("\n📝 Creating sample PDF...")
    
    try:
        import fitz  # PyMuPDF
        
        # Create sample PDF
        doc = fitz.open()
        page = doc.new_page()
        
        # Add sample text
        sample_text = """
Intelligent PDF Quick Link Query System Test Document

Company Information:
- Full Company Name: China Construction Bank Corporation
- Stock Abbreviation: CCB
- Stock Code: 601939
- Increase: 15.5%

Related Documents:
- 《Company Articles》
- 《Annual Report》

Responsible Persons: Zhang San, Li Si

Proposal Name: Proposal on Amending Company Articles
        """
        
        # Insert text
        page.insert_text((50, 50), sample_text, fontsize=12)
        
        # Save file
        sample_pdf_path = os.path.join(project_root, 'uploads', 'sample_test.pdf')
        doc.save(sample_pdf_path)
        doc.close()
        
        print(f"✅ Sample PDF created successfully: {sample_pdf_path}")
        return sample_pdf_path
        
    except Exception as e:
        print(f"❌ Failed to create sample PDF: {str(e)}")
        return None

def test_full_workflow():
    """Test complete workflow"""
    print("\n🔄 Testing complete workflow...")
    
    # Create sample PDF
    sample_pdf = create_sample_pdf()
    if not sample_pdf:
        print("❌ Unable to create sample PDF, skipping complete workflow test")
        return False
    
    try:
        # 1. PDF parsing
        processor = PDFProcessor()
        pages_data = processor.extract_text_with_positions(sample_pdf)
        print(f"✅ PDF parsing successful, total {len(pages_data)} pages")
        
        # 2. Information extraction
        extractor = LLMExtractor()
        query_types = ['stock_name', 'company_name', 'book_title', 'numbers']
        
        extracted_info = []
        for query_type in query_types:
            results = extractor._extract_with_rules(
                pages_data[0]['full_text'], 
                query_type, 
                1, 
                pages_data[0]
            )
            extracted_info.extend(results)
        
        print(f"✅ Information extraction successful, found {len(extracted_info)} items")
        
        # Display extraction results
        for item in extracted_info:
            print(f"   - {item['type']}: {item['value']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Intelligent PDF Quick Link Query System - Function Test")
    print("=" * 50)
    
    test_results = []
    
    # Run various tests
    test_results.append(("Configuration Test", test_config()))
    test_results.append(("PDF Processor Test", test_pdf_processor()))
    test_results.append(("LLM Extractor Test", test_llm_extractor()))
    test_results.append(("Local LLM Test", test_local_llm()))
    test_results.append(("Complete Workflow Test", test_full_workflow()))
    
    # Display test results
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ Passed" if result else "❌ Failed"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System functions normally")
        return True
    else:
        print("⚠️  Some tests failed, please check related configurations")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)