"""图片分类服务"""

import io
import os
from typing import Dict, List, Optional, Tuple
from PIL import Image
import aiofiles
from pathlib import Path

from ..models import ModelFactory, ClassificationResult
from ..utils.config import config_manager


class ImageClassifier:
    """图片分类器"""

    def __init__(self, model_type: Optional[str] = None):
        """
        初始化分类器

        Args:
            model_type: 模型类型，如果不指定则使用配置中的默认模型
        """
        self.model_type = model_type or config_manager.get_app_config().default_model
        self.config = config_manager.get_model_config(self.model_type)
        if not self.config:
            raise ValueError(f"Model configuration not found: {self.model_type}")

        self.model = ModelFactory.get_model(self.model_type, self.config.dict())

    async def classify_image_file(self, file_path: str) -> ClassificationResult:
        """
        分类图片文件

        Args:
            file_path: 图片文件路径

        Returns:
            ClassificationResult: 分类结果
        """
        # 读取图片文件
        async with aiofiles.open(file_path, 'rb') as f:
            image_data = await f.read()

        return await self.classify_image_data(image_data)

    async def classify_image_data(self, image_data: bytes) -> ClassificationResult:
        """
        分类图片数据

        Args:
            image_data: 图片二进制数据

        Returns:
            ClassificationResult: 分类结果
        """
        # 验证图片格式
        if not self._is_valid_image(image_data):
            return ClassificationResult(
                category="unknown",
                confidence=0.0,
                reasoning="Invalid image format or corrupted file",
                raw_response=""
            )

        # 获取分类配置
        categories = config_manager.get_categories()
        category_keywords = {
            name: category.keywords
            for name, category in categories.items()
        }

        # 使用模型分类
        result = await self.model.classify_image(image_data, category_keywords)

        return result

    def _is_valid_image(self, image_data: bytes) -> bool:
        """验证图片数据是否有效"""
        try:
            # 尝试打开图片
            image = Image.open(io.BytesIO(image_data))
            image.verify()  # 验证图片数据
            return True
        except Exception:
            return False

    @staticmethod
    def get_supported_formats() -> List[str]:
        """获取支持的图片格式"""
        return config_manager.get_app_config().supported_formats

    @staticmethod
    def get_max_file_size() -> int:
        """获取最大文件大小（MB）"""
        return config_manager.get_app_config().max_file_size

    @staticmethod
    def is_file_size_valid(file_size: int) -> bool:
        """检查文件大小是否有效"""
        max_size_bytes = ImageClassifier.get_max_file_size() * 1024 * 1024
        return file_size <= max_size_bytes

    @staticmethod
    def is_supported_format(filename: str) -> bool:
        """检查文件格式是否支持"""
        # 获取文件扩展名
        file_extension = Path(filename).suffix.lower().lstrip('.')
        return file_extension in ImageClassifier.get_supported_formats()


class BatchClassifier:
    """批量图片分类器"""

    def __init__(self, model_type: Optional[str] = None):
        self.classifier = ImageClassifier(model_type)

    async def classify_directory(self, directory_path: str) -> List[Tuple[str, ClassificationResult]]:
        """
        分类目录中的所有图片

        Args:
            directory_path: 目录路径

        Returns:
            List[Tuple[str, ClassificationResult]]: (文件名, 分类结果) 的列表
        """
        results = []
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")

        # 遍历目录中的所有文件
        for file_path in directory.rglob('*'):
            if file_path.is_file() and self.classifier.is_supported_format(file_path.name):
                try:
                    result = await self.classifier.classify_image_file(str(file_path))
                    results.append((str(file_path), result))
                except Exception as e:
                    # 如果分类失败，创建错误结果
                    error_result = ClassificationResult(
                        category="unknown",
                        confidence=0.0,
                        reasoning=f"Classification failed: {str(e)}",
                        raw_response=""
                    )
                    results.append((str(file_path), error_result))

        return results