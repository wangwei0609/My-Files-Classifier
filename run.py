#!/usr/bin/env python3
"""图片分类器启动脚本"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app.main import app


def main():
    """启动应用"""
    # 检查配置文件
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ 配置文件不存在: config.yaml")
        print("请参考 config.yaml.example 创建配置文件")
        sys.exit(1)

    # 检查环境变量
    required_env_vars = []
    config_path = Path("config.yaml")
    if config_path.exists():
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        default_model = config.get('app', {}).get('default_model', 'openai')
        if default_model in config.get('models', {}):
            api_key = config['models'][default_model].get('api_key', '')
            if api_key.startswith('${') and api_key.endswith('}'):
                env_var = api_key[2:-1]
                if ':' in env_var:
                    env_var = env_var.split(':')[0]
                required_env_vars.append(env_var)

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请设置相应的API密钥环境变量")
        print("参考 .env.example 文件")
        sys.exit(1)

    # 启动服务器
    print("🚀 启动图片分类器服务...")
    print("📊 访问地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")

    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"]
    )


if __name__ == "__main__":
    main()