"""Anthropic Claude模型实现"""

import base64
from typing import Dict, Any, List
import io
from PIL import Image

from .llm_base import BaseLLMModel, ClassificationResult

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicModel(BaseLLMModel):
    """Anthropic Claude模型"""

    def __init__(self, config: Dict[str, Any]):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")

        super().__init__(config)
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def classify_image(self, image_data: bytes, categories: Dict[str, List[str]]) -> ClassificationResult:
        """使用Anthropic Claude分类图片"""
        try:
            # 构建提示词
            prompt = self._build_prompt(categories)

            # 将图片转换为base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # 确定图片类型
            image_type = self._detect_image_type(image_data)

            # 调用Anthropic API
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": f"image/{image_type}",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )

            raw_response = response.content[0].text
            return self._parse_response(raw_response, categories)

        except Exception as e:
            # 返回错误结果
            return ClassificationResult(
                category="unknown",
                confidence=0.0,
                reasoning=f"Anthropic API error: {str(e)}",
                raw_response=""
            )

    def _detect_image_type(self, image_data: bytes) -> str:
        """检测图片类型"""
        try:
            import imghdr
            image_type = imghdr.what(None, h=image_data)
            return image_type if image_type else "jpeg"
        except ImportError:
            # 如果没有imghdr，默认返回jpeg
            return "jpeg"

    def _build_prompt(self, categories: Dict[str, List[str]]) -> str:
        """构建Anthropic分类提示词"""
        categories_text = "\n".join([
            f"- {category}: {', '.join(keywords)}"
            for category, keywords in categories.items()
        ])

        prompt = f"""Please analyze this image and classify it into one of the following categories:

{categories_text}

Instructions:
1. Look carefully at the image content
2. Identify the main subject or theme
3. Choose the most appropriate category based on the keywords
4. Respond with just the category name and a brief explanation

Format your response as:
Category: [category_name]
Reason: [brief explanation]"""

        return prompt