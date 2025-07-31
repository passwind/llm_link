import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """System Configuration Class"""
    
    # Basic configuration
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    
    # File upload configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # LLM configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # openai, deepseek, claude, local
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')  # Optional, for proxy
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # DeepSeek configuration
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    
    # Claude configuration
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
    
    # Local LLM configuration
    LOCAL_MODEL_PATH = os.getenv('LOCAL_MODEL_PATH', './models')
    LOCAL_MODEL_NAME = os.getenv('LOCAL_MODEL_NAME', 'chatglm3-6b')
    
    # Vector index configuration (optional)
    USE_VECTOR_INDEX = os.getenv('USE_VECTOR_INDEX', 'false').lower() == 'true'
    VECTOR_INDEX_PATH = os.path.join(BASE_DIR, 'models', 'vector_index')
    
    # Frontend configuration
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Debug configuration
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate if configuration is complete"""
        errors = []
        
        if cls.LLM_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            errors.append('OpenAI API Key not configured')
        
        if cls.LLM_PROVIDER == 'deepseek' and not cls.DEEPSEEK_API_KEY:
            errors.append('DeepSeek API Key not configured')
        
        if cls.LLM_PROVIDER == 'claude' and not cls.CLAUDE_API_KEY:
            errors.append('Claude API Key not configured')
        
        if cls.LLM_PROVIDER == 'local' and not os.path.exists(cls.LOCAL_MODEL_PATH):
            errors.append('Local model path does not exist')
        
        return errors
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
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
        """Get current LLM configuration information"""
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

# Create necessary directories
Config.create_directories()