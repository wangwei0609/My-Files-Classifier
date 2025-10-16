"""LLM模型基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel


class ClassificationResult(BaseModel):
    """分类结果"""
    category: str
    confidence: float
    reasoning: str
    raw_response: str


class BaseLLMModel(ABC):
    """LLM模型基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("model")
        self.api_key = config.get("api_key")
        self.max_tokens = config.get("max_tokens", 300)

    @abstractmethod
    async def classify_image(self, image_data: bytes, categories: Dict[str, List[str]]) -> ClassificationResult:
        """
        分类图片

        Args:
            image_data: 图片二进制数据
            categories: 分类配置，格式为 {category_name: [keywords]}

        Returns:
            ClassificationResult: 分类结果
        """
        pass

    @abstractmethod
    def _build_prompt(self, categories: Dict[str, List[str]]) -> str:
        """构建分类提示词"""
        pass

    def _parse_response(self, response: str, categories: Dict[str, List[str]]) -> ClassificationResult:
        """解析模型响应"""
        # 这是一个基础解析方法，子类可以重写
        response_lower = response.lower()

        # 计算每个类别的匹配度
        category_scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in response_lower:
                    score += 1
            category_scores[category] = score / len(keywords)

        # 选择得分最高的类别
        best_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[best_category]

        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            reasoning=f"Based on keyword matching in the response: {response[:100]}...",
            raw_response=response
        )