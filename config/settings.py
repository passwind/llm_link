import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""
    
    # 基础配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    
    # 文件上传配置
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # LLM配置
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # openai, deepseek, claude, local
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')  # 可选，用于代理
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # DeepSeek配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    # Claude配置
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
    
    # 本地LLM配置
    LOCAL_MODEL_PATH = os.getenv('LOCAL_MODEL_PATH', './models')
    LOCAL_MODEL_NAME = os.getenv('LOCAL_MODEL_NAME', 'chatglm3-6b')
    
    # 向量索引配置（可选）
    USE_VECTOR_INDEX = os.getenv('USE_VECTOR_INDEX', 'false').lower() == 'true'
    VECTOR_INDEX_PATH = os.path.join(BASE_DIR, 'models', 'vector_index')
    
    # 前端配置
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # 调试配置
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """验证配置是否完整"""
        errors = []
        
        if cls.LLM_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            errors.append('OpenAI API Key未配置')
        
        if cls.LLM_PROVIDER == 'deepseek' and not cls.DEEPSEEK_API_KEY:
            errors.append('DeepSeek API Key未配置')
        
        if cls.LLM_PROVIDER == 'claude' and not cls.CLAUDE_API_KEY:
            errors.append('Claude API Key未配置')
        
        if cls.LLM_PROVIDER == 'local' and not os.path.exists(cls.LOCAL_MODEL_PATH):
            errors.append('本地模型路径不存在')
        
        return errors
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        directories = [
            cls.UPLOAD_FOLDER,
            cls.STATIC_FOLDER,
            cls.LOCAL_MODEL_PATH,
            cls.VECTOR_INDEX_PATH
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_llm_config(cls):
        """获取当前LLM配置信息"""
        config_info = {
            'provider': cls.LLM_PROVIDER,
            'model': None,
            'api_configured': False
        }
        
        if cls.LLM_PROVIDER == 'openai':
            config_info['model'] = cls.OPENAI_MODEL
            config_info['api_configured'] = bool(cls.OPENAI_API_KEY)
        elif cls.LLM_PROVIDER == 'deepseek':
            config_info['model'] = cls.DEEPSEEK_MODEL
            config_info['api_configured'] = bool(cls.DEEPSEEK_API_KEY)
        elif cls.LLM_PROVIDER == 'claude':
            config_info['model'] = cls.CLAUDE_MODEL
            config_info['api_configured'] = bool(cls.CLAUDE_API_KEY)
        elif cls.LLM_PROVIDER == 'local':
            config_info['model'] = cls.LOCAL_MODEL_NAME
            config_info['api_configured'] = os.path.exists(cls.LOCAL_MODEL_PATH)
        
        return config_info

# 创建必要的目录
Config.create_directories()