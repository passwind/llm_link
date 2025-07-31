import fitz  # PyMuPDF
import json
from typing import List, Dict, Tuple

class PDFProcessor:
    """PDF文档处理器"""
    
    def __init__(self):
        self.current_doc = None
        self.pages_data = []
    
    def extract_text_with_positions(self, pdf_path: str) -> List[Dict]:
        """从PDF中提取文本和位置信息
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含每页文本和位置信息的列表
        """
        try:
            doc = fitz.open(pdf_path)
            self.current_doc = doc
            pages_data = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # 获取页面文本块
                text_blocks = page.get_text("dict")
                
                # 提取文本和位置信息
                page_info = {
                    'page_number': page_num + 1,
                    'page_size': {
                        'width': page.rect.width,
                        'height': page.rect.height
                    },
                    'text_blocks': [],
                    'full_text': ''
                }
                
                full_text_parts = []
                
                for block in text_blocks['blocks']:
                    if 'lines' in block:  # 文本块
                        for line in block['lines']:
                            for span in line['spans']:
                                text = span['text'].strip()
                                if text:
                                    bbox = span['bbox']  # [x0, y0, x1, y1]
                                    
                                    text_info = {
                                        'text': text,
                                        'bbox': {
                                            'x0': bbox[0],
                                            'y0': bbox[1],
                                            'x1': bbox[2],
                                            'y1': bbox[3]
                                        },
                                        'font_size': span['size'],
                                        'font_name': span['font'],
                                        'flags': span['flags']  # 字体样式标志
                                    }
                                    
                                    page_info['text_blocks'].append(text_info)
                                    full_text_parts.append(text)
                
                page_info['full_text'] = ' '.join(full_text_parts)
                pages_data.append(page_info)
            
            self.pages_data = pages_data
            doc.close()
            return pages_data
            
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")
    
    def get_text_by_page(self, page_number: int) -> str:
        """获取指定页面的文本
        
        Args:
            page_number: 页码（从1开始）
            
        Returns:
            页面文本内容
        """
        if not self.pages_data or page_number < 1 or page_number > len(self.pages_data):
            return ""
        
        return self.pages_data[page_number - 1]['full_text']
    
    def search_text_positions(self, search_text: str) -> List[Dict]:
        """搜索文本在PDF中的位置
        
        Args:
            search_text: 要搜索的文本
            
        Returns:
            包含匹配位置信息的列表
        """
        results = []
        
        for page_data in self.pages_data:
            page_number = page_data['page_number']
            
            for text_block in page_data['text_blocks']:
                if search_text.lower() in text_block['text'].lower():
                    result = {
                        'page': page_number,
                        'text': text_block['text'],
                        'position': {
                            'x': (text_block['bbox']['x0'] + text_block['bbox']['x1']) / 2,
                            'y': (text_block['bbox']['y0'] + text_block['bbox']['y1']) / 2
                        },
                        'bbox': text_block['bbox']
                    }
                    results.append(result)
        
        return results
    
    def get_context_around_position(self, page_number: int, target_bbox: Dict, context_range: int = 100) -> str:
        """获取指定位置周围的上下文文本
        
        Args:
            page_number: 页码
            target_bbox: 目标位置的边界框
            context_range: 上下文范围（像素）
            
        Returns:
            上下文文本
        """
        if page_number < 1 or page_number > len(self.pages_data):
            return ""
        
        page_data = self.pages_data[page_number - 1]
        context_texts = []
        
        target_y = (target_bbox['y0'] + target_bbox['y1']) / 2
        
        for text_block in page_data['text_blocks']:
            block_y = (text_block['bbox']['y0'] + text_block['bbox']['y1']) / 2
            
            # 检查是否在上下文范围内
            if abs(block_y - target_y) <= context_range:
                context_texts.append(text_block['text'])
        
        return ' '.join(context_texts)
    
    def get_page_count(self) -> int:
        """获取PDF页数"""
        return len(self.pages_data)
    
    def export_text_data(self, output_path: str):
        """导出文本数据到JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.pages_data, f, ensure_ascii=False, indent=2)