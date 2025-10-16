# 图片内容分类器 🖼️

一个基于多模态大模型的图片内容分类PoC项目，支持使用不同厂商的AI模型对图片内容进行智能分类。

## 功能特点

- 🤖 **多模型支持**: 支持OpenAI GPT-4V、Anthropic Claude、Google Gemini等多种多模态大模型
- 📁 **灵活配置**: 通过YAML配置文件管理分类规则和模型参数
- 🌐 **友好界面**: 简洁直观的Web界面，支持拖拽上传和批量处理
- ⚡ **异步处理**: 基于FastAPI的高性能异步架构
- 🔧 **易于扩展**: 模块化设计，轻松添加新的模型和分类规则

## 技术栈

- **后端**: Python 3.10+ + FastAPI
- **前端**: HTML/CSS/JavaScript (原生)
- **配置管理**: YAML + Pydantic
- **包管理**: UV
- **图像处理**: Pillow

## 项目结构

```
.
├── src/
│   ├── app/                    # FastAPI应用
│   │   ├── __init__.py
│   │   └── main.py            # 主应用文件
│   ├── models/                # LLM模型实现
│   │   ├── __init__.py
│   │   ├── llm_base.py        # 基础模型类
│   │   ├── openai_model.py    # OpenAI模型
│   │   ├── anthropic_model.py # Anthropic模型
│   │   └── model_factory.py   # 模型工厂
│   ├── services/              # 业务逻辑
│   │   ├── __init__.py
│   │   └── classifier.py      # 图片分类服务
│   └── utils/                 # 工具模块
│       ├── __init__.py
│       └── config.py          # 配置管理
├── templates/                 # HTML模板
│   └── index.html
├── static/                   # 静态文件
├── uploads/                  # 上传文件临时目录
├── config.yaml               # 配置文件
├── .env.example             # 环境变量示例
├── pyproject.toml           # 项目配置
└── run.py                   # 启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
# 使用uv安装基础依赖
uv sync

# 或安装特定模型的依赖
uv sync --extra openai    # OpenAI模型
uv sync --extra anthropic # Anthropic模型
uv sync --extra google    # Google模型
uv sync --extra all       # 安装所有模型支持
```

### 2. 配置环境变量

复制环境变量示例文件并配置API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加相应的API密钥：

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API Key
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. 配置分类规则

编辑 `config.yaml` 文件，自定义分类规则：

```yaml
image_categories:
  cat:
    keywords: ["cat", "kitten", "feline", "猫", "小猫", "猫咪"]
    description: "包含猫的图片"

  dog:
    keywords: ["dog", "puppy", "canine", "狗", "小狗", "狗狗"]
    description: "包含狗的图片"

# 更多分类...
```

### 4. 启动服务

```bash
# 使用启动脚本
python run.py

# 或直接使用uvicorn
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 使用说明

### Web界面使用

1. 打开浏览器访问 http://localhost:8000
2. 选择要使用的AI模型
3. 点击"选择文件"或直接拖拽图片到上传区域
4. 支持批量上传多张图片
5. 点击"开始分类"等待分析结果
6. 查看每张图片的分类结果和置信度

### API使用

#### 单张图片分类

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg" \
  -F "model=openai"
```

#### 批量图片分类

```bash
curl -X POST "http://localhost:8000/classify_batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "model=anthropic"
```

## 配置说明

### 模型配置

在 `config.yaml` 中配置不同模型的参数：

```yaml
models:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4-vision-preview"
    base_url: "https://api.openai.com/v1"
    max_tokens: 300

  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet-20240229"
    max_tokens: 300
```

### 分类规则配置

每个分类包含以下字段：

- `keywords`: 关键词列表，用于匹配模型响应
- `description`: 分类描述

## 扩展开发

### 添加新模型

1. 在 `src/models/` 目录下创建新的模型文件
2. 继承 `BaseLLMModel` 类并实现相应方法
3. 在 `ModelFactory` 中注册新模型
4. 在配置文件中添加模型配置

### 添加新分类

在 `config.yaml` 的 `image_categories` 部分添加新的分类规则。

## 常见问题

### Q: 如何添加新的图片格式支持？

A: 在 `config.yaml` 的 `app.supported_formats` 中添加新的格式。

### Q: 模型调用失败怎么办？

A: 检查API密钥是否正确配置，网络连接是否正常，以及模型配置参数是否正确。

### Q: 如何提高分类准确率？

A:
1. 优化关键词配置，使其更准确
2. 调整模型参数，如增加 `max_tokens`
3. 尝试不同的模型
4. 提供更详细的提示词

## 许可证

MIT License

## 贡献

欢迎提交Issues和Pull Requests！