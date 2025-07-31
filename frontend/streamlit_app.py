import streamlit as st
import requests
import json
import os
from pathlib import Path
import time
from typing import Dict, List, Any
import sys

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from i18n import t, set_language, get_language, get_supported_languages, get_language_name

# Configure page
st.set_page_config(
    page_title="Intelligent PDF Quick Link Query System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:5001/api"

class PDFQueryApp:
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state"""
        if 'uploaded_file_info' not in st.session_state:
            st.session_state.uploaded_file_info = None
        if 'extracted_info' not in st.session_state:
            st.session_state.extracted_info = []
        if 'selected_item' not in st.session_state:
            st.session_state.selected_item = None
        if 'language' not in st.session_state:
            st.session_state.language = 'zh'
    
    def render_header(self):
        """Render page header"""
        # Language selector
        col1, col2 = st.columns([4, 1])
        with col2:
            languages = get_supported_languages()
            current_lang = get_language()
            lang_options = {lang: get_language_name(lang) for lang in languages}
            
            selected_lang = st.selectbox(
                "Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(current_lang),
                key="language_selector"
            )
            
            if selected_lang != current_lang:
                set_language(selected_lang)
                st.session_state.language = selected_lang
                st.rerun()
        
        with col1:
            st.title(f"📄 {t('app.title')}")
        
        st.markdown(t('app.description'))
        st.divider()
    
    def render_sidebar(self):
        """Render sidebar"""
        with st.sidebar:
            st.header(f"🔧 {t('sidebar.settings')}")
            
            # Backend service status
            try:
                response = requests.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    st.success(f"✅ {t('status.connected')}")
                else:
                    st.error(f"❌ {t('status.error')}")
            except:
                st.error(f"❌ {t('status.disconnected')}")
            
            st.divider()
            
            # Query type selection
            st.subheader(f"📋 {t('query.title')}")
            try:
                response = requests.get(f"{API_BASE_URL}/query_types")
                if response.status_code == 200:
                    query_types_data = response.json()['query_types']
                    
                    selected_types = []
                    for query_type in query_types_data:
                        # Get translated name
                        type_name = query_type['name']
                        display_name = t(f'query.types.{type_name}', fallback=type_name)
                        
                        if st.checkbox(
                            display_name,
                            key=f"type_{query_type['id']}",
                            help=query_type['description']
                        ):
                            selected_types.append(query_type['id'])
                    
                    st.session_state.selected_query_types = selected_types
                else:
                    st.error(t('errors.network_error'))
            except Exception as e:
                st.error(f"{t('errors.network_error')}: {str(e)}")
            
            st.divider()
            
            # System information
            st.subheader(f"ℹ️ {t('sidebar.system_info')}")
            st.info(f"""
            **{t('sidebar.features')}:**
            - {t('sidebar.feature_upload')}
            - {t('sidebar.feature_extract')}
            - {t('sidebar.feature_locate')}
            - {t('sidebar.feature_display')}
            """)
    
    def render_file_upload(self):
        """Render file upload section"""
        st.header(f"📤 {t('upload.title')}")
        
        uploaded_file = st.file_uploader(
            t('upload.drag_drop'),
            type=['pdf'],
            help=f"{t('upload.supported_formats')}, {t('upload.max_size')}"
        )
        
        if uploaded_file is not None:
            # Display file information
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('upload.filename'), uploaded_file.name)
            with col2:
                st.metric(t('upload.file_size'), f"{uploaded_file.size / 1024 / 1024:.2f} MB")
            with col3:
                st.metric(t('upload.file_type'), uploaded_file.type)
            
            # Upload button
            if st.button(f"🚀 {t('upload.upload_and_parse')}", type="primary"):
                with st.spinner(t('upload.uploading')):
                    success = self.upload_file(uploaded_file)
                    if success:
                        st.success(f"✅ {t('upload.success')}")
                        st.rerun()
                    else:
                        st.error(f"❌ {t('upload.error')}")
    
    def upload_file(self, uploaded_file) -> bool:
        """Upload file to backend"""
        try:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.uploaded_file_info = result
                return True
            else:
                error_msg = response.json().get('error', t('errors.unknown_error'))
                st.error(f"{t('upload.error')}: {error_msg}")
                return False
        except Exception as e:
            st.error(f"{t('errors.unknown_error')}: {str(e)}")
            return False
    
    def render_extraction_section(self):
        """Render information extraction section"""
        if not st.session_state.uploaded_file_info:
            st.info(t('upload.upload_first'))
            return
        
        st.header(f"🔍 {t('extraction.title')}")
        
        # Display document information
        file_info = st.session_state.uploaded_file_info
        col1, col2 = st.columns(2)
        with col1:
            st.metric(t('extraction.document_name'), file_info['filename'])
        with col2:
            st.metric(t('extraction.pages'), file_info['pages'])
        
        # Extraction button
        if hasattr(st.session_state, 'selected_query_types') and st.session_state.selected_query_types:
            if st.button(f"🎯 {t('extraction.start_button')}", type="primary"):
                with st.spinner(t('extraction.processing')):
                    success = self.extract_information()
                    if success:
                        st.success(f"✅ {t('extraction.success')}")
                        st.rerun()
                    else:
                        st.error(f"❌ {t('extraction.error')}")
        else:
            st.warning(t('extraction.select_types'))
    
    def extract_information(self) -> bool:
        """Execute information extraction"""
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
                error_msg = response.json().get('error', t('errors.extraction_error'))
                st.error(f"{t('errors.extraction_error')}: {error_msg}")
                return False
        except Exception as e:
            st.error(f"{t('errors.unknown_error')}: {str(e)}")
            return False
    
    def render_results_section(self):
        """Render results display section"""
        if not st.session_state.extracted_info:
            return
        
        st.header(f"📊 {t('results.title')}")
        
        # Results statistics
        total_items = len(st.session_state.extracted_info)
        if total_items == 0:
            st.info(t('results.no_results'))
            return
        
        # Group statistics by type
        type_counts = {}
        for item in st.session_state.extracted_info:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        # Display statistics
        st.subheader(f"📈 {t('results.found_items', count=total_items)}")
        cols = st.columns(len(type_counts))
        for i, (type_name, count) in enumerate(type_counts.items()):
            with cols[i]:
                display_name = t(f'query.types.{type_name}', fallback=type_name)
                st.metric(display_name, count)
        
        st.divider()
        
        # Results list and details
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"📋 {t('results.list')}")
            self.render_results_list()
        
        with col2:
            st.subheader(f"🔍 {t('results.details')}")
            self.render_item_details()
    
    def render_results_list(self):
        """Render results list"""
        for i, item in enumerate(st.session_state.extracted_info):
            # Create clickable item
            container = st.container()
            with container:
                # Get translated type name
                type_name = item['type']
                display_name = t(f'query.types.{type_name}', fallback=type_name)
                
                if st.button(
                    f"**{display_name}**: {item['value']}",
                    key=f"item_{i}",
                    help=f"{t('results.page')}: {item['page']}",
                    use_container_width=True
                ):
                    st.session_state.selected_item = item
                    st.rerun()
                
                # Display brief information
                st.caption(f"📄 {t('results.page_number', page=item['page'])} | {item['context'][:50]}...")
                st.divider()
    
    def render_item_details(self):
        """Render selected item details"""
        if not st.session_state.selected_item:
            st.info(t('results.select_item'))
            return
        
        item = st.session_state.selected_item
        
        # Details card
        with st.container():
            # Get translated type name
            type_name = item['type']
            display_name = t(f'query.types.{type_name}', fallback=type_name)
            st.markdown(f"### {display_name}")
            
            # Basic information
            col1, col2 = st.columns(2)
            with col1:
                st.metric(t('results.extracted_value'), item['value'])
            with col2:
                st.metric(t('results.page'), item['page'])
            
            # Position information
            if item.get('position'):
                position = item['position']
                st.metric(t('results.position'), f"({position[0]:.1f}, {position[1]:.1f})")
            
            # Context
            st.subheader(f"📝 {t('results.context')}")
            st.text_area(
                t('results.full_context'),
                value=item['context'],
                height=150,
                disabled=True
            )
            
            # PDF view link (if available)
            if st.session_state.uploaded_file_info:
                filename = st.session_state.uploaded_file_info['filename']
                pdf_url = f"{API_BASE_URL}/pdf/{filename}"
                st.markdown(f"[📖 {t('results.view_pdf')}]({pdf_url})")
    
    def run(self):
        """Run application"""
        self.render_header()
        self.render_sidebar()
        
        # Main content area
        tab1, tab2 = st.tabs([f"📤 {t('upload.title')}", f"📊 {t('results.title')}"])
        
        with tab1:
            self.render_file_upload()
            self.render_extraction_section()
        
        with tab2:
            self.render_results_section()

if __name__ == "__main__":
    app = PDFQueryApp()
    app.run()