# 📄 智能PDF快速联动查询系统

基于LLM的智能PDF信息抽取系统，支持从PDF文档中快速抽取特定类型的信息，并提供联动查询和高亮显示功能。

## ✨ 主要功能

- 📤 **PDF文档上传和解析** - 支持PDF文档上传，使用PyMuPDF提取文本和位置信息
- 🎯 **智能信息抽取** - 基于LLM技术抽取证券简称、公司全称、人名、数字等特定信息
- 🔍 **多类型查询支持** - 支持证券简称、公司全称、人名、数字、书名号内容、提案议案等
- 🔗 **联动查询显示** - 左侧结果列表，右侧详细信息，支持位置定位
- 🤖 **多LLM支持** - 支持OpenAI GPT-4、DeepSeek、Claude、本地ChatGLM等
- 🎨 **友好用户界面** - 基于Streamlit的现代化Web界面

## 🏗️ 系统架构

```
ai_link/
├── backend/                 # 后端API服务
│   ├── app.py              # Flask主应用
│   ├── pdf_processor.py    # PDF处理模块
│   ├── llm_extractor.py    # LLM信息抽取
│   └── local_llm.py        # 本地LLM支持
├── frontend/               # 前端界面
│   └── streamlit_app.py    # Streamlit应用
├── config/                 # 配置文件
│   └── settings.py         # 系统配置
├── uploads/                # 上传文件目录
├── static/                 # 静态资源
├── models/                 # 本地模型目录
├── docs/                   # 文档
│   └── requirement.md      # 需求文档
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量模板
├── start.py               # 启动脚本
└── README.md              # 项目说明
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 推荐使用虚拟环境
- 可选：CUDA GPU（用于本地LLM）

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd ai_link

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
vim .env  # 或使用其他编辑器
```

配置示例：
```env
# 选择LLM提供商: openai, deepseek, claude, local
LLM_PROVIDER=openai

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# DeepSeek配置（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 其他配置...
```

### 4. 启动系统

```bash
# 启动完整系统（推荐）
python start.py --all

# 或分别启动
python start.py --backend   # 仅后端
python start.py --frontend  # 仅前端

# 检查系统状态
python start.py --check
```

### 5. 访问系统

- 🎨 **前端界面**: http://localhost:8501
- 🔧 **后端API**: http://localhost:5000
- 📊 **健康检查**: http://localhost:5000/api/health

## 📖 使用指南

### 基本使用流程

1. **上传PDF文档**
   - 在前端界面选择PDF文件
   - 点击"上传并解析"按钮
   - 系统自动解析文档结构

2. **选择查询类型**
   - 在侧边栏选择需要抽取的信息类型
   - 支持多选组合查询

3. **执行信息抽取**
   - 点击"开始信息抽取"按钮
   - LLM分析文档内容并抽取信息

4. **查看结果**
   - 左侧显示抽取结果列表
   - 点击项目查看详细信息
   - 包含位置坐标和上下文

### 支持的查询类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 证券简称 | 股票、基金等证券简称 | 建行、平安、茅台 |
| 公司全称 | 公司完整名称 | 中国建设银行股份有限公司 |
| 人名 | 人员姓名 | 张三、李四 |
| 数字 | 金额、百分比、代码等 | 100万元、15.5%、600036 |
| 书名号内容 | 《》内的文字 | 《公司法》、《年度报告》 |
| 提案/议案名 | 提案或议案名称 | 关于修改公司章程的议案 |

## 🤖 LLM配置说明

### OpenAI GPT-4
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

### DeepSeek
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...
```

### Claude
```env
LLM_PROVIDER=claude
CLAUDE_API_KEY=sk-ant-...
```

### 本地LLM（ChatGLM等）
```env
LLM_PROVIDER=local
LOCAL_MODEL_PATH=./models
LOCAL_MODEL_NAME=chatglm3-6b
```

#### 本地模型下载

```bash
# ChatGLM3-6B
git lfs install
git clone https://huggingface.co/THUDM/chatglm3-6b ./models/chatglm3-6b

# Qwen-1.5-7B
git clone https://huggingface.co/Qwen/Qwen1.5-7B-Chat ./models/qwen1.5-7b
```

**硬件要求**：
- GPU内存：≥ 8GB（推荐16GB+）
- 系统内存：≥ 16GB
- 磁盘空间：≥ 20GB

## 🔧 API接口文档

### 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data

参数：
- file: PDF文件

响应：
{
  "success": true,
  "filename": "document.pdf",
  "filepath": "/path/to/file",
  "pages": 10
}
```

### 信息抽取
```http
POST /api/extract
Content-Type: application/json

请求体：
{
  "filepath": "/path/to/file",
  "query_types": ["stock_name", "company_name"]
}

响应：
{
  "success": true,
  "extracted_info": [
    {
      "type": "证券简称",
      "value": "建行",
      "context": "本报告由建行提供",
      "page": 3,
      "position": [100, 250]
    }
  ]
}
```

### 查询类型
```http
GET /api/query_types

响应：
{
  "query_types": [
    {
      "id": "stock_name",
      "name": "证券简称",
      "description": "股票、基金等证券的简称"
    }
  ]
}
```

## 🛠️ 开发指南

### 项目结构说明

- **backend/app.py**: Flask主应用，提供RESTful API
- **backend/pdf_processor.py**: PDF解析模块，使用PyMuPDF
- **backend/llm_extractor.py**: LLM信息抽取核心逻辑
- **backend/local_llm.py**: 本地LLM支持模块
- **frontend/streamlit_app.py**: Streamlit前端界面
- **config/settings.py**: 系统配置管理

### 添加新的查询类型

1. 在`llm_extractor.py`中添加类型描述
2. 在`app.py`中更新查询类型列表
3. 根据需要添加规则抽取逻辑

### 添加新的LLM支持

1. 在`config/settings.py`中添加配置项
2. 在`llm_extractor.py`中实现对应的抽取方法
3. 更新环境变量模板

## 🔍 故障排除

### 常见问题

**Q: 后端启动失败**
```bash
# 检查端口占用
lsof -i :5000

# 检查依赖安装
pip list | grep -E "flask|PyMuPDF"
```

**Q: LLM API调用失败**
- 检查API密钥配置
- 确认网络连接
- 查看API配额限制

**Q: 本地模型加载失败**
- 检查模型文件完整性
- 确认GPU内存充足
- 查看CUDA版本兼容性

**Q: PDF解析失败**
- 确认PDF文件未损坏
- 检查文件大小限制
- 尝试其他PDF文件

### 日志查看

```bash
# 后端日志
python backend/app.py

# 前端日志
streamlit run frontend/streamlit_app.py --logger.level=debug
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF处理
- [Streamlit](https://streamlit.io/) - 前端框架
- [Flask](https://flask.palletsprojects.com/) - 后端框架
- [Transformers](https://huggingface.co/transformers/) - 本地LLM支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues]
- 💬 Discussions: [GitHub Discussions]

---

**智能PDF快速联动查询系统** - 让文档信息抽取更智能、更高效！