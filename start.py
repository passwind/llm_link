#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能PDF快速联动查询系统启动脚本

使用方法：
1. 仅启动后端API: python start.py --backend
2. 仅启动前端界面: python start.py --frontend  
3. 同时启动前后端: python start.py --all
4. 检查系统状态: python start.py --check
"""

import argparse
import subprocess
import sys
import os
import time
import requests
from multiprocessing import Process

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查系统依赖...")
    
    required_packages = [
        'flask', 'streamlit', 'PyMuPDF', 'requests', 
        'python-dotenv', 'flask-cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖检查通过")
    return True

def check_config():
    """检查配置文件"""
    print("\n🔧 检查配置文件...")
    
    # 检查.env文件
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("⚠️  .env文件不存在，请复制.env.example并配置")
            print("运行: cp .env.example .env")
        else:
            print("❌ 配置文件模板不存在")
        return False
    
    # 检查必要目录
    directories = ['uploads', 'static', 'models']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"📁 创建目录: {directory}")
        else:
            print(f"✅ 目录存在: {directory}")
    
    print("✅ 配置检查完成")
    return True

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端API服务...")
    
    try:
        # 切换到backend目录
        backend_path = os.path.join(os.getcwd(), 'backend')
        
        # 启动Flask应用
        subprocess.run([
            sys.executable, 'app.py'
        ], cwd=backend_path, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  后端服务已停止")
    except Exception as e:
        print(f"❌ 后端启动失败: {str(e)}")

def start_frontend():
    """启动前端服务"""
    print("🎨 启动前端界面...")
    
    try:
        # 启动Streamlit应用
        subprocess.run([
            'streamlit', 'run', 'frontend/streamlit_app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  前端服务已停止")
    except Exception as e:
        print(f"❌ 前端启动失败: {str(e)}")

def start_all():
    """同时启动前后端"""
    print("🚀 启动完整系统...")
    
    # 启动后端进程
    backend_process = Process(target=start_backend)
    backend_process.start()
    
    # 等待后端启动
    print("⏳ 等待后端服务启动...")
    time.sleep(3)
    
    # 检查后端是否启动成功
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务启动成功")
        else:
            print("⚠️  后端服务可能未正常启动")
    except:
        print("⚠️  无法连接到后端服务")
    
    # 启动前端
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n⏹️  正在停止所有服务...")
        backend_process.terminate()
        backend_process.join()
        print("✅ 所有服务已停止")

def check_system():
    """检查系统状态"""
    print("🔍 检查系统状态...")
    
    # 检查后端
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务 (http://localhost:5000) - 运行正常")
        else:
            print("⚠️  后端服务 - 响应异常")
    except:
        print("❌ 后端服务 (http://localhost:5000) - 未运行")
    
    # 检查前端
    try:
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务 (http://localhost:8501) - 运行正常")
        else:
            print("⚠️  前端服务 - 响应异常")
    except:
        print("❌ 前端服务 (http://localhost:8501) - 未运行")

def show_usage():
    """显示使用说明"""
    usage_text = """
📄 智能PDF快速联动查询系统

🚀 快速启动：
  python start.py --all          # 启动完整系统
  python start.py --backend      # 仅启动后端API
  python start.py --frontend     # 仅启动前端界面
  python start.py --check        # 检查系统状态

🔗 访问地址：
  前端界面: http://localhost:8501
  后端API:  http://localhost:5000
  API文档:  http://localhost:5000/api/health

📋 使用步骤：
  1. 配置.env文件（复制.env.example）
  2. 安装依赖: pip install -r requirements.txt
  3. 启动系统: python start.py --all
  4. 打开浏览器访问前端界面
  5. 上传PDF文档并选择查询类型
  6. 查看抽取结果和联动显示

💡 提示：
  - 首次使用请确保已配置LLM API密钥
  - 支持OpenAI、DeepSeek、Claude等多种LLM
  - 可选择使用本地部署的LLM模型
    """
    print(usage_text)

def main():
    parser = argparse.ArgumentParser(
        description='智能PDF快速联动查询系统启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--backend', action='store_true', help='仅启动后端API服务')
    parser.add_argument('--frontend', action='store_true', help='仅启动前端界面')
    parser.add_argument('--all', action='store_true', help='启动完整系统（推荐）')
    parser.add_argument('--check', action='store_true', help='检查系统状态')
    parser.add_argument('--no-check', action='store_true', help='跳过依赖检查')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，显示使用说明
    if not any([args.backend, args.frontend, args.all, args.check]):
        show_usage()
        return
    
    # 检查系统状态
    if args.check:
        check_system()
        return
    
    # 检查依赖和配置（除非跳过）
    if not args.no_check:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_config():
            sys.exit(1)
    
    # 根据参数启动相应服务
    try:
        if args.all:
            start_all()
        elif args.backend:
            start_backend()
        elif args.frontend:
            start_frontend()
    except KeyboardInterrupt:
        print("\n👋 感谢使用智能PDF快速联动查询系统！")

if __name__ == '__main__':
    main()