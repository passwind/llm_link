#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent PDF Quick Link Query System Startup Script

Usage:
1. Start backend API only: python start.py --backend
2. Start frontend interface only: python start.py --frontend  
3. Start both frontend and backend: python start.py --all
4. Check system status: python start.py --check
"""

import argparse
import subprocess
import sys
import os
import time
import requests
from multiprocessing import Process

def check_dependencies():
    """Check if dependencies are installed"""
    print("🔍 Checking system dependencies...")
    
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
        print(f"\n⚠️  Missing the following dependency packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies check passed")
    return True

def check_config():
    """Check configuration files"""
    print("\n🔧 Checking configuration files...")
    
    # Check .env file
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("⚠️  .env file does not exist, please copy .env.example and configure")
            print("Run: cp .env.example .env")
        else:
            print("❌ Configuration file template does not exist")
        return False
    
    # Check necessary directories
    directories = ['uploads', 'static', 'models']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    print("✅ Configuration check completed")
    return True

def start_backend():
    """Start backend service"""
    print("🚀 Starting backend API service...")
    
    try:
        # Switch to backend directory
        backend_path = os.path.join(os.getcwd(), 'backend')
        
        # Start Flask application
        subprocess.run([
            sys.executable, 'app.py'
        ], cwd=backend_path, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Backend service stopped")
    except Exception as e:
        print(f"❌ Backend startup failed: {str(e)}")

def start_frontend():
    """Start frontend service"""
    print("🎨 Starting frontend interface...")
    
    try:
        # Start Streamlit application
        subprocess.run([
            'streamlit', 'run', 'frontend/streamlit_app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Frontend service stopped")
    except Exception as e:
        print(f"❌ Frontend startup failed: {str(e)}")

def start_all():
    """Start both frontend and backend"""
    print("🚀 Starting complete system...")
    
    # Start backend process
    backend_process = Process(target=start_backend)
    backend_process.start()
    
    # Wait for backend to start
    print("⏳ Waiting for backend service to start...")
    time.sleep(3)
    
    # Check if backend started successfully
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend service started successfully")
        else:
            print("⚠️  Backend service may not have started normally")
    except:
        print("⚠️  Unable to connect to backend service")
    
    # Start frontend
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping all services...")
        backend_process.terminate()
        backend_process.join()
        print("✅ All services stopped")

def check_system():
    """Check system status"""
    print("🔍 Checking system status...")
    
    # Check backend
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend service (http://localhost:5000) - Running normally")
        else:
            print("⚠️  Backend service - Abnormal response")
    except:
        print("❌ Backend service (http://localhost:5000) - Not running")
    
    # Check frontend
    try:
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend service (http://localhost:8501) - Running normally")
        else:
            print("⚠️  Frontend service - Abnormal response")
    except:
        print("❌ Frontend service (http://localhost:8501) - Not running")

def show_usage():
    """Show usage instructions"""
    usage_text = """
📄 Intelligent PDF Quick Link Query System

🚀 Quick Start:
  python start.py --all          # Start complete system
  python start.py --backend      # Start backend API only
  python start.py --frontend     # Start frontend interface only
  python start.py --check        # Check system status

🔗 Access URLs:
  Frontend interface: http://localhost:8501
  Backend API:  http://localhost:5000
  API docs:  http://localhost:5000/api/health

📋 Usage Steps:
  1. Configure .env file (copy .env.example)
  2. Install dependencies: pip install -r requirements.txt
  3. Start system: python start.py --all
  4. Open browser and access frontend interface
  5. Upload PDF documents and select query type
  6. View extraction results and linked display

💡 Tips:
  - Please ensure LLM API key is configured for first use
  - Supports multiple LLMs like OpenAI, DeepSeek, Claude
  - Option to use locally deployed LLM models
    """
    print(usage_text)

def main():
    parser = argparse.ArgumentParser(
        description='Intelligent PDF Quick Link Query System Startup Script',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--backend', action='store_true', help='Start backend API service only')
    parser.add_argument('--frontend', action='store_true', help='Start frontend interface only')
    parser.add_argument('--all', action='store_true', help='Start complete system (recommended)')
    parser.add_argument('--check', action='store_true', help='Check system status')
    parser.add_argument('--no-check', action='store_true', help='Skip dependency check')
    
    args = parser.parse_args()
    
    # If no parameters specified, show usage instructions
    if not any([args.backend, args.frontend, args.all, args.check]):
        show_usage()
        return
    
    # Check system status
    if args.check:
        check_system()
        return
    
    # Check dependencies and configuration (unless skipped)
    if not args.no_check:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_config():
            sys.exit(1)
    
    # Start corresponding services based on parameters
    try:
        if args.all:
            start_all()
        elif args.backend:
            start_backend()
        elif args.frontend:
            start_frontend()
    except KeyboardInterrupt:
        print("\n👋 Thank you for using the Intelligent PDF Quick Link Query System!")

if __name__ == '__main__':
    main()