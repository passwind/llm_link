#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本

用于测试PDF处理、LLM抽取等核心功能
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
    """测试配置"""
    print("🔧 测试系统配置...")
    
    try:
        config = Config()
        print(f"✅ 上传目录: {config.UPLOAD_FOLDER}")
        print(f"✅ LLM提供商: {config.LLM_PROVIDER}")
        
        # 检查配置验证
        errors = config.validate_config()
        if errors:
            print("⚠️  配置警告:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ 配置验证通过")
        
        # 获取LLM配置信息
        llm_config = config.get_llm_config()
        print(f"✅ LLM配置: {llm_config}")
        
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        return False

def test_pdf_processor():
    """测试PDF处理器"""
    print("\n📄 测试PDF处理器...")
    
    try:
        processor = PDFProcessor()
        print("✅ PDF处理器初始化成功")
        
        # 测试基本方法
        page_count = processor.get_page_count()
        print(f"✅ 页数获取方法: {page_count}")
        
        return True
    except Exception as e:
        print(f"❌ PDF处理器测试失败: {str(e)}")
        return False

def test_llm_extractor():
    """测试LLM抽取器"""
    print("\n🤖 测试LLM抽取器...")
    
    try:
        extractor = LLMExtractor()
        print("✅ LLM抽取器初始化成功")
        
        # 测试规则抽取（不依赖API）
        test_text = "本报告由《中国建设银行》提供，股票代码601939，涨幅15.5%。"
        
        # 模拟页面数据
        page_data = {
            'page_number': 1,
            'text_blocks': [
                {
                    'text': test_text,
                    'bbox': {'x0': 100, 'y0': 200, 'x1': 300, 'y1': 220}
                }
            ]
        }
        
        # 测试书名号抽取
        results = extractor._extract_with_rules(test_text, 'book_title', 1, page_data)
        print(f"✅ 书名号抽取测试: 找到 {len(results)} 个结果")
        
        # 测试数字抽取
        results = extractor._extract_with_rules(test_text, 'numbers', 1, page_data)
        print(f"✅ 数字抽取测试: 找到 {len(results)} 个结果")
        
        return True
    except Exception as e:
        print(f"❌ LLM抽取器测试失败: {str(e)}")
        return False

def test_local_llm():
    """测试本地LLM（如果可用）"""
    print("\n🏠 测试本地LLM...")
    
    try:
        from backend.local_llm import LocalLLMManager
        
        manager = LocalLLMManager()
        print("✅ 本地LLM管理器初始化成功")
        
        # 获取模型信息
        model_info = manager.get_model_info()
        print(f"✅ 模型信息: {json.dumps(model_info, indent=2, ensure_ascii=False)}")
        
        # 检查是否有可用的本地模型
        model_path = model_info['model_path']
        if os.path.exists(model_path):
            print(f"✅ 模型目录存在: {model_path}")
            
            # 列出可用模型
            models = [d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))]
            if models:
                print(f"✅ 可用模型: {models}")
            else:
                print("⚠️  模型目录为空，请下载模型")
        else:
            print(f"⚠️  模型目录不存在: {model_path}")
        
        return True
    except Exception as e:
        print(f"❌ 本地LLM测试失败: {str(e)}")
        return False

def create_sample_pdf():
    """创建示例PDF文件用于测试"""
    print("\n📝 创建示例PDF...")
    
    try:
        import fitz  # PyMuPDF
        
        # 创建示例PDF
        doc = fitz.open()
        page = doc.new_page()
        
        # 添加示例文本
        sample_text = """
智能PDF快速联动查询系统测试文档

公司信息：
- 公司全称：中国建设银行股份有限公司
- 证券简称：建行
- 股票代码：601939
- 涨幅：15.5%

相关文件：
- 《公司章程》
- 《年度报告》

负责人：张三、李四

提案名称：关于修改公司章程的议案
        """
        
        # 插入文本
        page.insert_text((50, 50), sample_text, fontsize=12)
        
        # 保存文件
        sample_pdf_path = os.path.join(project_root, 'uploads', 'sample_test.pdf')
        doc.save(sample_pdf_path)
        doc.close()
        
        print(f"✅ 示例PDF创建成功: {sample_pdf_path}")
        return sample_pdf_path
        
    except Exception as e:
        print(f"❌ 创建示例PDF失败: {str(e)}")
        return None

def test_full_workflow():
    """测试完整工作流程"""
    print("\n🔄 测试完整工作流程...")
    
    # 创建示例PDF
    sample_pdf = create_sample_pdf()
    if not sample_pdf:
        print("❌ 无法创建示例PDF，跳过完整流程测试")
        return False
    
    try:
        # 1. PDF解析
        processor = PDFProcessor()
        pages_data = processor.extract_text_with_positions(sample_pdf)
        print(f"✅ PDF解析成功，共 {len(pages_data)} 页")
        
        # 2. 信息抽取
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
        
        print(f"✅ 信息抽取成功，共找到 {len(extracted_info)} 条信息")
        
        # 显示抽取结果
        for item in extracted_info:
            print(f"   - {item['type']}: {item['value']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整流程测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🧪 智能PDF快速联动查询系统 - 功能测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("配置测试", test_config()))
    test_results.append(("PDF处理器测试", test_pdf_processor()))
    test_results.append(("LLM抽取器测试", test_llm_extractor()))
    test_results.append(("本地LLM测试", test_local_llm()))
    test_results.append(("完整流程测试", test_full_workflow()))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)