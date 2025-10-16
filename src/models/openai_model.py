"""OpenAI GPT-4 Vision模型实现"""

import base64
from typing import Dict, Any, List
import io
from PIL import Image

from .llm_base import BaseLLMModel, ClassificationResult

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIModel(BaseLLMModel):
    """OpenAI GPT-4 Vision模型"""

    def __init__(self, config: Dict[str, Any]):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        super().__init__(config)
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=config.get("base_url")
        )

    async def classify_image(self, image_data: bytes, categories: Dict[str, List[str]]) -> ClassificationResult:
        """使用OpenAI GPT-4 Vision分类图片"""
        try:
            # 构建提示词
            prompt = self._build_prompt(categories)

            # 准备图片数据
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens
            )

            raw_response = response.choices[0].message.content
            return self._parse_response(raw_response, categories)

        except Exception as e:
            # 返回错误结果
            return ClassificationResult(
                category="unknown",
                confidence=0.0,
                reasoning=f"OpenAI API error: {str(e)}",
                raw_response=""
            )

    def _build_prompt(self, categories: Dict[str, List[str]]) -> str:
        """构建OpenAI分类提示词"""
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