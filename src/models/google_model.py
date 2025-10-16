"""Google Gemini模型实现"""

import base64
from typing import Dict, Any, List
import io
from PIL import Image

from .llm_base import BaseLLMModel, ClassificationResult

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleModel(BaseLLMModel):
    """Google Gemini模型"""

    def __init__(self, config: Dict[str, Any]):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Generative AI library not installed. Install with: pip install google-generativeai")

        super().__init__(config)

        # 配置Google API
        genai.configure(api_key=self.api_key)

        # 初始化模型
        self.model = genai.GenerativeModel(self.model_name)

    async def classify_image(self, image_data: bytes, categories: Dict[str, List[str]]) -> ClassificationResult:
        """使用Google Gemini分类图片"""
        try:
            # 构建提示词
            prompt = self._build_prompt(categories)

            # 准备图片数据
            image = Image.open(io.BytesIO(image_data))

            # 调用Google Gemini API
            response = await self.model.generate_content_async([prompt, image])

            raw_response = response.text
            return self._parse_response(raw_response, categories)

        except Exception as e:
            # 返回错误结果
            return ClassificationResult(
                category="unknown",
                confidence=0.0,
                reasoning=f"Google API error: {str(e)}",
                raw_response=""
            )

    def _build_prompt(self, categories: Dict[str, List[str]]) -> str:
        """构建Google分类提示词"""
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