"""配置文件管理模块"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from dataclasses import dataclass
from dotenv import load_dotenv


class ImageCategory(BaseModel):
    """图片分类配置"""
    keywords: List[str]
    description: str


class ModelConfig(BaseModel):
    """模型配置"""
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: int = 300


class AppConfig(BaseModel):
    """应用配置"""
    default_model: str = "openai"
    supported_formats: List[str] = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
    max_file_size: int = 10  # MB


class Config(BaseModel):
    """总配置"""
    image_categories: Dict[str, ImageCategory]
    models: Dict[str, ModelConfig]
    app: AppConfig


@dataclass
class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config.yaml"):
        # 加载环境变量
        load_dotenv()
        self.config_path = Path(config_path)
        self._config: Optional[Config] = None
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # 处理环境变量
        config_data = self._substitute_env_vars(config_data)

        self._config = Config(**config_data)

    def _substitute_env_vars(self, data: Any) -> Any:
        """递归替换配置中的环境变量"""
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            env_var = data[2:-1]
            default_value = None
            if ':' in env_var:
                env_var, default_value = env_var.split(':', 1)
            return os.getenv(env_var, default_value)
        return data

    @property
    def config(self) -> Config:
        """获取配置"""
        if self._config is None:
            self.load_config()
        return self._config

    def get_categories(self) -> Dict[str, ImageCategory]:
        """获取图片分类配置"""
        return self.config.image_categories

    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """获取指定模型配置"""
        return self.config.models.get(model_name)

    def get_app_config(self) -> AppConfig:
        """获取应用配置"""
        return self.config.app

    def reload(self) -> None:
        """重新加载配置"""
        self.load_config()


# 全局配置管理器实例
config_manager = ConfigManager()