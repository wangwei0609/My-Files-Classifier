"""模型工厂类"""

from typing import Dict, Any, Optional
from .llm_base import BaseLLMModel
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel
from .google_model import GoogleModel


class ModelFactory:
    """模型工厂类"""

    _models: Dict[str, BaseLLMModel] = {}

    @classmethod
    def create_model(cls, model_type: str, config: Dict[str, Any]) -> BaseLLMModel:
        """创建模型实例"""
        if model_type == "openai":
            return OpenAIModel(config)
        elif model_type == "anthropic":
            return AnthropicModel(config)
        elif model_type == "google":
            return GoogleModel(config)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    @classmethod
    def get_model(cls, model_type: str, config: Dict[str, Any]) -> BaseLLMModel:
        """获取模型实例（单例模式）"""
        if model_type not in cls._models:
            cls._models[model_type] = cls.create_model(model_type, config)
        return cls._models[model_type]

    @classmethod
    def get_available_models(cls) -> list[str]:
        """获取可用模型列表"""
        return ["openai", "anthropic", "google"]