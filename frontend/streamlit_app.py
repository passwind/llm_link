import streamlit as st
import requests
import json
import os
from typing import List, Dict
import base64
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="智能PDF快速联动查询系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 后端API地址
API_BASE_URL = "http://localhost:5001/api"

class PDFQueryApp:
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """初始化会话状态"""
        if 'uploaded_file_info' not in st.session_state:
            st.session_state.uploaded_file_info = None
        if 'extracted_info' not in st.session_state:
            st.session_state.extracted_info = []
        if 'selected_item' not in st.session_state:
            st.session_state.selected_item = None
    
    def render_header(self):
        """渲染页面头部"""
        st.title("📄 智能PDF快速联动查询系统")
        st.markdown("""
        这是一个基于LLM的智能PDF信息抽取系统，支持从PDF文档中快速抽取特定类型的信息，
        并提供联动查询和高亮显示功能。
        """)
        st.divider()
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.header("🔧 系统配置")
            
            # LLM配置状态
            try:
                response = requests.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    st.success("✅ 后端服务正常")
                else:
                    st.error("❌ 后端服务异常")
            except:
                st.error("❌ 无法连接后端服务")
            
            st.divider()
            
            # 查询类型选择
            st.subheader("📋 查询类型")
            try:
                response = requests.get(f"{API_BASE_URL}/query_types")
                if response.status_code == 200:
                    query_types_data = response.json()['query_types']
                    
                    selected_types = []
                    for query_type in query_types_data:
                        if st.checkbox(
                            query_type['name'],
                            key=f"type_{query_type['id']}",
                            help=query_type['description']
                        ):
                            selected_types.append(query_type['id'])
                    
                    st.session_state.selected_query_types = selected_types
                else:
                    st.error("无法获取查询类型")
            except Exception as e:
                st.error(f"获取查询类型失败: {str(e)}")
            
            st.divider()
            
            # 系统信息
            st.subheader("ℹ️ 系统信息")
            st.info("""
            **支持的功能：**
            - PDF文档上传和解析
            - 多种信息类型抽取
            - 智能位置定位
            - 联动查询显示
            """)
    
    def render_file_upload(self):
        """渲染文件上传区域"""
        st.header("📤 文档上传")
        
        uploaded_file = st.file_uploader(
            "选择PDF文件",
            type=['pdf'],
            help="支持上传PDF格式的文档，最大50MB"
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("文件名", uploaded_file.name)
            with col2:
                st.metric("文件大小", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
            with col3:
                st.metric("文件类型", uploaded_file.type)
            
            # 上传按钮
            if st.button("🚀 上传并解析", type="primary"):
                with st.spinner("正在上传和解析PDF文档..."):
                    success = self.upload_file(uploaded_file)
                    if success:
                        st.success("✅ PDF文档上传和解析成功！")
                        st.rerun()
                    else:
                        st.error("❌ 文档上传失败，请重试")
    
    def upload_file(self, uploaded_file) -> bool:
        """上传文件到后端"""
        try:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.uploaded_file_info = result
                return True
            else:
                st.error(f"上传失败: {response.json().get('error', '未知错误')}")
                return False
        except Exception as e:
            st.error(f"上传过程中发生错误: {str(e)}")
            return False
    
    def render_extraction_section(self):
        """渲染信息抽取区域"""
        if not st.session_state.uploaded_file_info:
            st.info("请先上传PDF文档")
            return
        
        st.header("🔍 信息抽取")
        
        # 显示文档信息
        file_info = st.session_state.uploaded_file_info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("文档名称", file_info['filename'])
        with col2:
            st.metric("页数", file_info['pages'])
        
        # 抽取按钮
        if hasattr(st.session_state, 'selected_query_types') and st.session_state.selected_query_types:
            if st.button("🎯 开始信息抽取", type="primary"):
                with st.spinner("正在使用LLM抽取信息，请稍候..."):
                    success = self.extract_information()
                    if success:
                        st.success("✅ 信息抽取完成！")
                        st.rerun()
                    else:
                        st.error("❌ 信息抽取失败，请重试")
        else:
            st.warning("请在侧边栏选择至少一种查询类型")
    
    def extract_information(self) -> bool:
        """执行信息抽取"""
        try:
            data = {
                'filepath': st.session_state.uploaded_file_info['filepath'],
                'query_types': st.session_state.selected_query_types
            }
            
            response = requests.post(f"{API_BASE_URL}/extract", json=data)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.extracted_info = result['extracted_info']
                return True
            else:
                st.error(f"抽取失败: {response.json().get('error', '未知错误')}")
                return False
        except Exception as e:
            st.error(f"抽取过程中发生错误: {str(e)}")
            return False
    
    def render_results_section(self):
        """渲染结果展示区域"""
        if not st.session_state.extracted_info:
            return
        
        st.header("📊 抽取结果")
        
        # 结果统计
        total_items = len(st.session_state.extracted_info)
        if total_items == 0:
            st.info("未找到匹配的信息")
            return
        
        # 按类型分组统计
        type_counts = {}
        for item in st.session_state.extracted_info:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        # 显示统计信息
        st.subheader(f"📈 共找到 {total_items} 条信息")
        cols = st.columns(len(type_counts))
        for i, (type_name, count) in enumerate(type_counts.items()):
            with cols[i]:
                st.metric(type_name, count)
        
        st.divider()
        
        # 结果列表和详情
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 信息列表")
            self.render_results_list()
        
        with col2:
            st.subheader("🔍 详细信息")
            self.render_item_details()
    
    def render_results_list(self):
        """渲染结果列表"""
        for i, item in enumerate(st.session_state.extracted_info):
            # 创建可点击的项目
            container = st.container()
            with container:
                if st.button(
                    f"**{item['type']}**: {item['value']}",
                    key=f"item_{i}",
                    help=f"页码: {item['page']}",
                    use_container_width=True
                ):
                    st.session_state.selected_item = item
                    st.rerun()
                
                # 显示简要信息
                st.caption(f"📄 第{item['page']}页 | {item['context'][:50]}...")
                st.divider()
    
    def render_item_details(self):
        """渲染选中项目的详细信息"""
        if not st.session_state.selected_item:
            st.info("点击左侧列表中的项目查看详细信息")
            return
        
        item = st.session_state.selected_item
        
        # 详细信息卡片
        with st.container():
            st.markdown(f"### {item['type']}")
            
            # 基本信息
            col1, col2 = st.columns(2)
            with col1:
                st.metric("抽取值", item['value'])
            with col2:
                st.metric("页码", item['page'])
            
            # 位置信息
            if item.get('position'):
                position = item['position']
                st.metric("位置坐标", f"({position[0]:.1f}, {position[1]:.1f})")
            
            # 上下文
            st.subheader("📝 上下文")
            st.text_area(
                "完整上下文",
                value=item['context'],
                height=150,
                disabled=True
            )
            
            # PDF查看链接（如果可用）
            if st.session_state.uploaded_file_info:
                filename = st.session_state.uploaded_file_info['filename']
                pdf_url = f"{API_BASE_URL}/pdf/{filename}"
                st.markdown(f"[📖 查看原始PDF文档]({pdf_url})")
    
    def run(self):
        """运行应用"""
        self.render_header()
        self.render_sidebar()
        
        # 主要内容区域
        tab1, tab2 = st.tabs(["📤 文档处理", "📊 结果查看"])
        
        with tab1:
            self.render_file_upload()
            self.render_extraction_section()
        
        with tab2:
            self.render_results_section()

if __name__ == "__main__":
    app = PDFQueryApp()
    app.run()