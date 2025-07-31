#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能PDF快速联动查询系统演示脚本

展示系统的核心功能和API使用方法
"""

import requests
import json
import os
from pathlib import Path

# API配置
API_BASE_URL = "http://localhost:5001/api"

def demo_health_check():
    """演示健康检查"""
    print("🔍 检查系统健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print("❌ 系统健康检查失败")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {str(e)}")
        return False

def demo_query_types():
    """演示查询类型获取"""
    print("\n📋 获取支持的查询类型...")
    try:
        response = requests.get(f"{API_BASE_URL}/query_types")
        if response.status_code == 200:
            result = response.json()
            print("✅ 支持的查询类型:")
            for query_type in result['query_types']:
                print(f"   - {query_type['name']}: {query_type['description']}")
            return result['query_types']
        else:
            print("❌ 获取查询类型失败")
            return []
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return []

def demo_file_upload():
    """演示文件上传"""
    print("\n📤 演示PDF文件上传...")
    
    # 使用测试生成的示例PDF
    sample_pdf_path = "uploads/sample_test.pdf"
    
    if not os.path.exists(sample_pdf_path):
        print("❌ 示例PDF文件不存在，请先运行测试脚本生成")
        return None
    
    try:
        with open(sample_pdf_path, 'rb') as f:
            files = {'file': ('sample_test.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文件上传成功: {result['filename']}")
            print(f"   页数: {result['pages']}")
            return result
        else:
            error = response.json().get('error', '未知错误')
            print(f"❌ 文件上传失败: {error}")
            return None
    except Exception as e:
        print(f"❌ 上传过程中发生错误: {str(e)}")
        return None

def demo_information_extraction(file_info):
    """演示信息抽取"""
    print("\n🎯 演示信息抽取...")
    
    if not file_info:
        print("❌ 没有可用的文件信息")
        return
    
    # 选择要抽取的信息类型
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
            
            print(f"✅ 信息抽取完成，共找到 {len(extracted_info)} 条信息:")
            
            # 按类型分组显示
            type_groups = {}
            for item in extracted_info:
                item_type = item['type']
                if item_type not in type_groups:
                    type_groups[item_type] = []
                type_groups[item_type].append(item)
            
            for type_name, items in type_groups.items():
                print(f"\n   📊 {type_name} ({len(items)}条):")
                for item in items:
                    print(f"      - {item['value']} (第{item['page']}页)")
                    print(f"        上下文: {item['context'][:50]}...")
            
            return extracted_info
        else:
            error = response.json().get('error', '未知错误')
            print(f"❌ 信息抽取失败: {error}")
            return []
    except Exception as e:
        print(f"❌ 抽取过程中发生错误: {str(e)}")
        return []

def demo_usage_guide():
    """演示使用指南"""
    guide = """
🎯 智能PDF快速联动查询系统使用指南

📖 基本使用流程:
1. 启动系统: python start.py --all
2. 访问前端: http://localhost:8501
3. 上传PDF文档
4. 选择查询类型
5. 执行信息抽取
6. 查看结果和联动显示

🔧 API使用示例:
1. 健康检查: GET /api/health
2. 获取查询类型: GET /api/query_types
3. 上传文件: POST /api/upload
4. 信息抽取: POST /api/extract

💡 支持的信息类型:
- 证券简称: 股票、基金等简称
- 公司全称: 完整的公司名称
- 人名: 人员姓名
- 数字: 金额、百分比、代码等
- 书名号内容: 《》内的文字
- 提案/议案名: 提案或议案名称

🤖 LLM配置:
- OpenAI GPT-4: 最高精度
- DeepSeek: 中文支持好
- Claude: 平衡性能
- 本地模型: 完全离线

🌐 访问地址:
- 前端界面: http://localhost:8501
- 后端API: http://localhost:5001
    """
    print(guide)

def main():
    """主演示函数"""
    print("🚀 智能PDF快速联动查询系统 - 功能演示")
    print("=" * 60)
    
    # 1. 健康检查
    if not demo_health_check():
        print("\n❌ 系统未正常运行，请先启动后端服务")
        print("运行: python start.py --backend")
        return
    
    # 2. 查询类型演示
    query_types = demo_query_types()
    
    # 3. 文件上传演示
    file_info = demo_file_upload()
    
    # 4. 信息抽取演示
    if file_info:
        extracted_info = demo_information_extraction(file_info)
    
    # 5. 使用指南
    print("\n" + "=" * 60)
    demo_usage_guide()
    
    print("\n🎉 演示完成！")
    print("\n💡 提示:")
    print("   - 访问 http://localhost:8501 使用Web界面")
    print("   - 查看 README.md 了解详细使用说明")
    print("   - 运行 python tests/test_system.py 进行系统测试")

if __name__ == '__main__':
    main()