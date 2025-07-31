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
    """LLM Information Extractor"""
    
    def __init__(self):
        self.config = Config()
        self.setup_llm_clients()
    
    def setup_llm_clients(self):
        """Setup LLM clients"""
        # OpenAI客户端
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
            if self.config.OPENAI_BASE_URL:
                openai.api_base = self.config.OPENAI_BASE_URL
    
    def extract_information(self, pages_data: List[Dict], query_types: List[str]) -> List[Dict]:
        """Extract specified types of information from PDF page data
        
        Args:
            pages_data: PDF page data
            query_types: List of query types
            
        Returns:
            List of extracted information
        """
        all_extracted = []
        
        for page_data in pages_data:
            page_number = page_data['page_number']
            page_text = page_data['full_text']
            
            if not page_text.strip():
                continue
            
            # Extract information for each query type
            for query_type in query_types:
                extracted_items = self._extract_by_type(page_text, query_type, page_number, page_data)
                all_extracted.extend(extracted_items)
        
        return all_extracted
    
    def _extract_by_type(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """Extract information by type
        
        Args:
            text: Page text
            query_type: Query type
            page_number: Page number
            page_data: Page data
            
        Returns:
            List of extracted information items
        """
        if self.config.LLM_PROVIDER == 'openai':
            return self._extract_with_openai(text, query_type, page_number, page_data)
        elif self.config.LLM_PROVIDER == 'deepseek':
            return self._extract_with_deepseek(text, query_type, page_number, page_data)
        else:
            # Use rule-based method as fallback
            return self._extract_with_rules(text, query_type, page_number, page_data)
    
    def _extract_with_openai(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """Extract information using OpenAI API"""
        try:
            prompt = self._build_extraction_prompt(text, query_type)
            
            response = openai.ChatCompletion.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional document information extraction assistant. Please strictly return results in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            return self._parse_llm_response(result_text, query_type, page_number, page_data)
            
        except Exception as e:
            print(f"OpenAI API call failed: {str(e)}")
            return self._extract_with_rules(text, query_type, page_number, page_data)
    
    def _extract_with_deepseek(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """Extract information using DeepSeek API"""
        try:
            prompt = self._build_extraction_prompt(text, query_type)
            
            headers = {
                'Authorization': f'Bearer {self.config.DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {"role": "system", "content": "You are a professional document information extraction assistant. Please strictly return results in JSON format."},
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
                raise Exception(f"API request failed: {response.status_code}")
                
        except Exception as e:
            print(f"DeepSeek API call failed: {str(e)}")
            return self._extract_with_rules(text, query_type, page_number, page_data)
    
    def _build_extraction_prompt(self, text: str, query_type: str) -> str:
        """Build information extraction prompt"""
        type_descriptions = {
            'stock_name': 'Security abbreviations (e.g., CCB, Ping An, Moutai and other stock abbreviations)',
            'company_name': 'Full company names (e.g., China Construction Bank Corporation)',
            'person_name': 'Person names (e.g., Zhang San, Li Si and other personnel names)',
            'numbers': 'Numerical information (e.g., amounts, percentages, codes, etc.)',
            'book_title': 'Text content within book title marks 《》',
            'proposal': 'Proposal or motion names'
        }
        
        description = type_descriptions.get(query_type, query_type)
        
        prompt = f"""Please extract all {description} from the following text and return results in JSON format.

Requirements:
1. Return format must be a JSON array
2. Each item contains: value (extracted value), context (context containing the complete sentence with the value)
3. If no relevant information is found, return empty array []
4. Ensure extracted information is accurate and avoid misjudgment

Text content:
{text}

Please return results in JSON format:"""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """Parse LLM response results"""
        try:
            # Try to extract JSON part
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted_data = json.loads(json_str)
            else:
                # If no JSON found, try direct parsing
                extracted_data = json.loads(response_text)
            
            results = []
            for item in extracted_data:
                if isinstance(item, dict) and 'value' in item:
                    # Find text position in page
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
            print(f"Failed to parse LLM response: {str(e)}")
            return []
    
    def _extract_with_rules(self, text: str, query_type: str, page_number: int, page_data: Dict) -> List[Dict]:
        """Extract information using rule-based method (fallback solution)"""
        results = []
        
        if query_type == 'book_title':
            # Extract book title content
            pattern = r'《([^》]+)》'
            matches = re.finditer(pattern, text)
            for match in matches:
                value = match.group(1)
                context = self._get_context(text, match.start(), match.end())
                position = self._find_text_position(value, page_data)
                
                results.append({
                    'type': 'Book Title Content',
                    'value': value,
                    'context': context,
                    'page': page_number,
                    'position': position
                })
        
        elif query_type == 'numbers':
            # Extract numerical information
            patterns = [
                r'\d+\.\d+%',  # Percentages
                r'\d+(?:,\d{3})*(?:\.\d+)?(?:万|亿|元)',  # Amounts
                r'\d{6}',  # Codes
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    value = match.group(0)
                    context = self._get_context(text, match.start(), match.end())
                    position = self._find_text_position(value, page_data)
                    
                    results.append({
                        'type': 'Number',
                        'value': value,
                        'context': context,
                        'page': page_number,
                        'position': position
                    })
        
        return results
    
    def _find_text_position(self, search_text: str, page_data: Dict) -> List[float]:
        """Find text position in page data"""
        for text_block in page_data['text_blocks']:
            if search_text in text_block['text']:
                bbox = text_block['bbox']
                return [(bbox['x0'] + bbox['x1']) / 2, (bbox['y0'] + bbox['y1']) / 2]
        
        return [0, 0]  # Default position
    
    def _get_context(self, text: str, start: int, end: int, context_length: int = 50) -> str:
        """Get context of matched text"""
        context_start = max(0, start - context_length)
        context_end = min(len(text), end + context_length)
        return text[context_start:context_end].strip()
    
    def _get_type_name(self, query_type: str) -> str:
        """Get Chinese name of query type"""
        type_names = {
            'stock_name': 'Security Abbreviation',
            'company_name': 'Company Full Name',
            'person_name': 'Person Name',
            'numbers': 'Number',
            'book_title': 'Book Title Content',
            'proposal': 'Proposal/Motion Name'
        }
        return type_names.get(query_type, query_type)