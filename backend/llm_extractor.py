import openai
import requests
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import Config

class LLMExtractor:
    """LLM信息抽取器"""
    
    def __init__(self):
        self.config = Config()
        self.setup_llm_clients()
    
    def setup_llm_clients(self):
        """设置LLM客户端"""
        # OpenAI客户端
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
            if self.config.OPENAI_BASE_URL:
                openai.api_base = self.config.OPENAI_BASE_URL
    
    def extract_information(self, pages_data: List[Dict], query_types: List[str]) -> List[Dict]:
        """从PDF页面数据中抽取指定类型的信息
        
        Args:
            pages_data: PDF页面数据
            query_types: 查询类型列表
            
        Returns:
            抽取的信息列表
        """
        all_extracted = []
        
        for page_data in pages_data:
            page_number = page_data['page_number']
            page_text = page_data['full_text']
            
            if not page_text.strip():
                continue
            
            # 为每种查询类型抽取信息
            for query_type in query_types:
                extracted_items = self._extract_by_type(page_text, query_type, page_number, page_data)
                all_extracted.extend(extracted_items)
        
        return all_extracted
    
    def _extract_by_type(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """根据类型抽取信息
        
        Args:
            text: 页面文本
            query_type: 查询类型
            page_number: 页码
            page_data: 页面数据
            
        Returns:
            抽取的信息项列表
        """
        if self.config.LLM_PROVIDER == 'openai':
            return self._extract_with_openai(text, query_type, page_number, page_data)
        elif self.config.LLM_PROVIDER == 'deepseek':
            return self._extract_with_deepseek(text, query_type, page_number, page_data)
        else:
            # 使用规则方法作为后备
            return self._extract_with_rules(text, query_type, page_number, page_data)
    
    def _extract_with_openai(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """使用OpenAI API抽取信息"""
        try:
            prompt = self._build_extraction_prompt(text, query_type)
            
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档信息抽取助手，请严格按照JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            return self._parse_llm_response(result_text, query_type, page_number, page_data)
            
        except Exception as e:
            print(f"OpenAI API调用失败: {str(e)}")
            return self._extract_with_rules(text, query_type, page_number, page_data)
    
    def _extract_with_deepseek(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """使用DeepSeek API抽取信息"""
        try:
            prompt = self._build_extraction_prompt(text, query_type)
            
            headers = {
                'Authorization': f'Bearer {self.config.DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {"role": "system", "content": "你是一个专业的文档信息抽取助手，请严格按照JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 2000
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                result_text = result['choices'][0]['message']['content'].strip()
                return self._parse_llm_response(result_text, query_type, page_number, page_data)
            else:
                raise Exception(f"API请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"DeepSeek API调用失败: {str(e)}")
            return self._extract_with_rules(text, query_type, page_number, page_data)
    
    def _build_extraction_prompt(self, text: str, query_type: str) -> str:
        """构建信息抽取提示词"""
        type_descriptions = {
            'stock_name': '证券简称（如：建行、平安、茅台等股票简称）',
            'company_name': '公司全称（如：中国建设银行股份有限公司）',
            'person_name': '人名（如：张三、李四等人员姓名）',
            'numbers': '数字信息（如：金额、百分比、代码等）',
            'book_title': '书名号《》内的文字内容',
            'proposal': '提案或议案名称'
        }
        
        description = type_descriptions.get(query_type, query_type)
        
        prompt = f"""请从以下文本中抽取所有的{description}，并返回JSON格式的结果。

要求：
1. 返回格式必须是JSON数组
2. 每个项目包含：value（抽取的值）、context（上下文，包含该值的完整句子）
3. 如果没有找到相关信息，返回空数组[]
4. 确保抽取的信息准确，避免误判

文本内容：
{text}

请返回JSON格式的结果："""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """解析LLM响应结果"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted_data = json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试直接解析
                extracted_data = json.loads(response_text)
            
            results = []
            for item in extracted_data:
                if isinstance(item, dict) and 'value' in item:
                    # 查找文本在页面中的位置
                    position = self._find_text_position(item['value'], page_data)
                    
                    result = {
                        'type': self._get_type_name(query_type),
                        'value': item['value'],
                        'context': item.get('context', ''),
                        'page': page_number,
                        'position': position
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"解析LLM响应失败: {str(e)}")
            return []
    
    def _extract_with_rules(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """使用规则方法抽取信息（后备方案）"""
        results = []
        
        if query_type == 'book_title':
            # 抽取书名号内容
            pattern = r'《([^》]+)》'
            matches = re.finditer(pattern, text)
            for match in matches:
                value = match.group(1)
                context = self._get_context(text, match.start(), match.end())
                position = self._find_text_position(value, page_data)
                
                results.append({
                    'type': '书名号内容',
                    'value': value,
                    'context': context,
                    'page': page_number,
                    'position': position
                })
        
        elif query_type == 'numbers':
            # 抽取数字信息
            patterns = [
                r'\d+\.\d+%',  # 百分比
                r'\d+(?:,\d{3})*(?:\.\d+)?(?:万|亿|元)',  # 金额
                r'\d{6}',  # 代码
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    value = match.group(0)
                    context = self._get_context(text, match.start(), match.end())
                    position = self._find_text_position(value, page_data)
                    
                    results.append({
                        'type': '数字',
                        'value': value,
                        'context': context,
                        'page': page_number,
                        'position': position
                    })
        
        return results
    
    def _find_text_position(self, search_text: str, page_data: Dict) -> List[float]:
        """在页面数据中查找文本位置"""
        for text_block in page_data['text_blocks']:
            if search_text in text_block['text']:
                bbox = text_block['bbox']
                return [(bbox['x0'] + bbox['x1']) / 2, (bbox['y0'] + bbox['y1']) / 2]
        
        return [0, 0]  # 默认位置
    
    def _get_context(self, text: str, start: int, end: int, context_length: int = 50) -> str:
        """获取匹配文本的上下文"""
        context_start = max(0, start - context_length)
        context_end = min(len(text), end + context_length)
        return text[context_start:context_end].strip()
    
    def _get_type_name(self, query_type: str) -> str:
        """获取查询类型的中文名称"""
        type_names = {
            'stock_name': '证券简称',
            'company_name': '公司全称',
            'person_name': '人名',
            'numbers': '数字',
            'book_title': '书名号内容',
            'proposal': '提案/议案名'
        }
        return type_names.get(query_type, query_type)