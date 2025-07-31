import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
import json
import re
from typing import List, Dict, Optional
from config.settings import Config

class LocalLLMManager:
    """本地LLM管理器"""
    
    def __init__(self):
        self.config = Config()
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_loaded = False
    
    def load_model(self, model_name: str = None) -> bool:
        """加载本地模型
        
        Args:
            model_name: 模型名称，如果为None则使用配置中的默认模型
            
        Returns:
            是否加载成功
        """
        try:
            if model_name is None:
                model_name = self.config.LOCAL_MODEL_NAME
            
            model_path = f"{self.config.LOCAL_MODEL_PATH}/{model_name}"
            
            print(f"正在加载模型: {model_path}")
            
            # 根据模型类型选择加载方式
            if 'chatglm' in model_name.lower():
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_path, 
                    trust_remote_code=True
                )
                self.model = AutoModel.from_pretrained(
                    model_path, 
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                ).to(self.device)
            else:
                # 通用的因果语言模型加载方式
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                ).to(self.device)
            
            # 设置为评估模式
            self.model.eval()
            self.model_loaded = True
            
            print(f"模型加载成功，设备: {self.device}")
            return True
            
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            self.model_loaded = False
            return False
    
    def generate_response(self, prompt: str, max_length: int = 2048, temperature: float = 0.1) -> str:
        """生成响应
        
        Args:
            prompt: 输入提示
            max_length: 最大生成长度
            temperature: 温度参数
            
        Returns:
            生成的响应文本
        """
        if not self.model_loaded:
            raise Exception("模型未加载")
        
        try:
            with torch.no_grad():
                if 'chatglm' in self.config.LOCAL_MODEL_NAME.lower():
                    # ChatGLM特殊处理
                    response, _ = self.model.chat(
                        self.tokenizer,
                        prompt,
                        max_length=max_length,
                        temperature=temperature
                    )
                    return response
                else:
                    # 通用生成方式
                    inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
                    
                    outputs = self.model.generate(
                        inputs,
                        max_length=max_length,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                    
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    # 移除输入部分
                    response = response[len(prompt):].strip()
                    return response
                    
        except Exception as e:
            raise Exception(f"生成响应失败: {str(e)}")
    
    def extract_information_local(self, text: str, query_type: str) -> List[Dict]:
        """使用本地模型抽取信息
        
        Args:
            text: 输入文本
            query_type: 查询类型
            
        Returns:
            抽取的信息列表
        """
        if not self.model_loaded:
            return []
        
        try:
            prompt = self._build_extraction_prompt_local(text, query_type)
            response = self.generate_response(prompt)
            return self._parse_local_response(response, query_type)
            
        except Exception as e:
            print(f"本地模型抽取失败: {str(e)}")
            return []
    
    def _build_extraction_prompt_local(self, text: str, query_type: str) -> str:
        """构建本地模型的抽取提示"""
        type_descriptions = {
            'stock_name': '证券简称（如：建行、平安、茅台等股票简称）',
            'company_name': '公司全称（如：中国建设银行股份有限公司）',
            'person_name': '人名（如：张三、李四等人员姓名）',
            'numbers': '数字信息（如：金额、百分比、代码等）',
            'book_title': '书名号《》内的文字内容',
            'proposal': '提案或议案名称'
        }
        
        description = type_descriptions.get(query_type, query_type)
        
        prompt = f"""请从以下文本中抽取所有的{description}。

要求：
1. 返回JSON格式的数组
2. 每个项目包含：value（抽取的值）、context（包含该值的完整句子）
3. 如果没有找到相关信息，返回空数组[]
4. 确保抽取准确，避免误判

文本内容：
{text}

请返回JSON格式结果："""
        
        return prompt
    
    def _parse_local_response(self, response: str, query_type: str) -> List[Dict]:
        """解析本地模型响应"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                extracted_data = json.loads(json_str)
            else:
                # 如果没有找到JSON，返回空列表
                return []
            
            results = []
            for item in extracted_data:
                if isinstance(item, dict) and 'value' in item:
                    result = {
                        'type': self._get_type_name(query_type),
                        'value': item['value'],
                        'context': item.get('context', ''),
                        'confidence': item.get('confidence', 0.8)  # 默认置信度
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"解析本地模型响应失败: {str(e)}")
            return []
    
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
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            'model_name': self.config.LOCAL_MODEL_NAME,
            'model_path': self.config.LOCAL_MODEL_PATH,
            'device': str(self.device),
            'loaded': self.model_loaded,
            'cuda_available': torch.cuda.is_available(),
            'gpu_memory': torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0
        }
    
    def unload_model(self):
        """卸载模型释放内存"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.model_loaded = False
        print("模型已卸载")

# 全局模型管理器实例
local_llm_manager = LocalLLMManager()

def download_model_guide():
    """模型下载指南"""
    guide = """
    本地模型下载指南：
    
    1. ChatGLM3-6B:
       ```bash
       # 使用git lfs下载
       git lfs install
       git clone https://huggingface.co/THUDM/chatglm3-6b ./models/chatglm3-6b
       ```
    
    2. Qwen-1.5-7B:
       ```bash
       git clone https://huggingface.co/Qwen/Qwen1.5-7B-Chat ./models/qwen1.5-7b
       ```
    
    3. 使用Python下载：
       ```python
       from transformers import AutoTokenizer, AutoModel
       
       model_name = "THUDM/chatglm3-6b"
       tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
       model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
       
       # 保存到本地
       tokenizer.save_pretrained("./models/chatglm3-6b")
       model.save_pretrained("./models/chatglm3-6b")
       ```
    
    注意：
    - 确保有足够的磁盘空间（通常需要10-20GB）
    - 建议使用GPU进行推理（至少8GB显存）
    - 首次下载可能需要较长时间
    """
    return guide