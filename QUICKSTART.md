# 快速启动指南 🚀

## 1️⃣ 项目安装

```bash
# 安装基础依赖
uv sync

# 安装OpenAI模型支持（推荐）
uv sync --extra openai

# 或安装所有模型支持
uv sync --extra all
```

## 2️⃣ 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加你的API密钥
# 例如：OPENAI_API_KEY=sk-your-key-here
```

## 3️⃣ 测试系统

```bash
# 运行测试脚本
python test_example.py
```

## 4️⃣ 启动服务

```bash
# 启动Web服务
python run.py
```

## 5️⃣ 使用系统

- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🎯 5分钟快速体验

1. 访问 http://localhost:8000
2. 选择一个AI模型（如OpenAI）
3. 上传一张图片（支持jpg、png等格式）
4. 点击"开始分类"
5. 查看AI分析结果！

## 📝 自定义分类

编辑 `config.yaml` 文件中的 `image_categories` 部分：

```yaml
image_categories:
  your_category:
    keywords: ["keyword1", "keyword2", "关键词1"]
    description: "你的分类描述"
```

## 🔧 故障排除

- **配置错误**: 检查 `config.yaml` 和 `.env` 文件
- **API调用失败**: 确认API密钥有效且有足够额度
- **文件格式不支持**: 检查图片格式是否在配置的支持列表中