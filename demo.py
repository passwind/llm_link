#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent PDF Quick Link Query System Demo Script

Demonstrates the core functionality and API usage of the system
"""

import requests
import json
import os
from pathlib import Path

# API配置
API_BASE_URL = "http://localhost:5001/api"

def demo_health_check():
    """Demonstrate health check"""
    print("🔍 Checking system health status...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print("❌ System health check failed")
            return False
    except Exception as e:
        print(f"❌ Unable to connect to backend service: {str(e)}")
        return False

def demo_query_types():
    """Demonstrate query types retrieval"""
    print("\n📋 Getting supported query types...")
    try:
        response = requests.get(f"{API_BASE_URL}/query_types")
        if response.status_code == 200:
            result = response.json()
            print("✅ Supported query types:")
            for query_type in result['query_types']:
                print(f"   - {query_type['name']}: {query_type['description']}")
            return result['query_types']
        else:
            print("❌ Failed to get query types")
            return []
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return []

def demo_file_upload():
    """Demonstrate file upload"""
    print("\n📤 Demonstrating PDF file upload...")
    
    # Use test-generated sample PDF
    sample_pdf_path = "uploads/sample_test.pdf"
    
    if not os.path.exists(sample_pdf_path):
        print("❌ Sample PDF file does not exist, please run test script to generate it first")
        return None
    
    try:
        with open(sample_pdf_path, 'rb') as f:
            files = {'file': ('sample_test.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File uploaded successfully: {result['filename']}")
            print(f"   Pages: {result['pages']}")
            return result
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ File upload failed: {error}")
            return None
    except Exception as e:
        print(f"❌ Error occurred during upload: {str(e)}")
        return None

def demo_information_extraction(file_info):
    """Demonstrate information extraction"""
    print("\n🎯 Demonstrating information extraction...")
    
    if not file_info:
        print("❌ No available file information")
        return
    
    # Select information types to extract
    query_types = ['stock_name', 'company_name', 'numbers', 'book_title']
    
    try:
        data = {
            'filepath': file_info['filepath'],
            'query_types': query_types
        }
        
        response = requests.post(f"{API_BASE_URL}/extract", json=data)
        
        if response.status_code == 200:
            result = response.json()
            extracted_info = result['extracted_info']
            
            print(f"✅ Information extraction completed, found {len(extracted_info)} items:")
            
            # Group by type for display
            type_groups = {}
            for item in extracted_info:
                item_type = item['type']
                if item_type not in type_groups:
                    type_groups[item_type] = []
                type_groups[item_type].append(item)
            
            for type_name, items in type_groups.items():
                print(f"\n   📊 {type_name} ({len(items)} items):")
                for item in items:
                    print(f"      - {item['value']} (Page {item['page']})")
                    print(f"        Context: {item['context'][:50]}...")
            
            return extracted_info
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Information extraction failed: {error}")
            return []
    except Exception as e:
        print(f"❌ Error occurred during extraction: {str(e)}")
        return []

def demo_usage_guide():
    """Demonstrate usage guide"""
    guide = """
🎯 Intelligent PDF Quick Link Query System Usage Guide

📖 Basic Usage Flow:
1. Start system: python start.py --all
2. Access frontend: http://localhost:8501
3. Upload PDF documents
4. Select query types
5. Execute information extraction
6. View results and linked display

🔧 API Usage Examples:
1. Health check: GET /api/health
2. Get query types: GET /api/query_types
3. Upload file: POST /api/upload
4. Information extraction: POST /api/extract

💡 Supported Information Types:
- Stock abbreviations: Stock, fund abbreviations
- Company full names: Complete company names
- Person names: Personnel names
- Numbers: Amounts, percentages, codes, etc.
- Book title content: Text within 《》
- Proposal/motion names: Proposal or motion names

🤖 LLM Configuration:
- OpenAI GPT-4: Highest accuracy
- DeepSeek: Good Chinese support
- Claude: Balanced performance
- Local models: Completely offline

🌐 Access Addresses:
- Frontend interface: http://localhost:8501
- Backend API: http://localhost:5001
    """
    print(guide)

def main():
    """Main demo function"""
    print("🚀 Intelligent PDF Quick Link Query System - Function Demo")
    print("=" * 60)
    
    # 1. Health check
    if not demo_health_check():
        print("\n❌ System not running properly, please start backend service first")
        print("Run: python start.py --backend")
        return
    
    # 2. Query types demo
    query_types = demo_query_types()
    
    # 3. File upload demo
    file_info = demo_file_upload()
    
    # 4. Information extraction demo
    if file_info:
        extracted_info = demo_information_extraction(file_info)
    
    # 5. Usage guide
    print("\n" + "=" * 60)
    demo_usage_guide()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Tips:")
    print("   - Visit http://localhost:8501 to use Web interface")
    print("   - Check README.md for detailed usage instructions")
    print("   - Run python tests/test_system.py for system testing")

if __name__ == '__main__':
    main()