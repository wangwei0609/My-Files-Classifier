"""FastAPI主应用"""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..services import ImageClassifier
from ..models import ModelFactory
from ..utils.config import config_manager

# 创建FastAPI应用
app = FastAPI(
    title="Image Classifier",
    description="A PoC for image content classification using multimodal LLMs",
    version="0.1.0"
)

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 确保上传目录存在
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 分类结果数据模型
class ClassificationResultResponse(BaseModel):
    """分类结果响应模型"""
    filename: str
    category: str
    confidence: float
    reasoning: str
    model_used: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "supported_formats": ImageClassifier.get_supported_formats(),
        "max_file_size": ImageClassifier.get_max_file_size(),
        "available_models": ModelFactory.get_available_models()
    })


@app.post("/classify", response_model=ClassificationResultResponse)
async def classify_image(
    request: Request,
    file: UploadFile = File(...),
    model: Optional[str] = Form(None)
):
    """
    分类上传的图片
    """
    try:
        # 验证文件
        if not ImageClassifier.is_supported_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {ImageClassifier.get_supported_formats()}"
            )

        # 读取文件数据
        file_data = await file.read()

        # 验证文件大小
        if not ImageClassifier.is_file_size_valid(len(file_data)):
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {ImageClassifier.get_max_file_size()}MB"
            )

        # 保存文件到临时位置
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        temp_filename = f"{file_id}{file_extension}"
        temp_filepath = UPLOAD_DIR / temp_filename

        with open(temp_filepath, "wb") as f:
            f.write(file_data)

        try:
            # 创建分类器
            classifier = ImageClassifier(model)

            # 分类图片
            result = await classifier.classify_image_data(file_data)

            # 构建响应
            response = ClassificationResultResponse(
                filename=file.filename,
                category=result.category,
                confidence=result.confidence,
                reasoning=result.reasoning,
                model_used=classifier.model_type
            )

            return response

        finally:
            # 清理临时文件
            if temp_filepath.exists():
                temp_filepath.unlink()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/classify_batch")
async def classify_multiple_images(
    request: Request,
    files: List[UploadFile] = File(...),
    model: Optional[str] = Form(None)
):
    """
    批量分类上传的图片
    """
    results = []
    errors = []

    for file in files:
        try:
            # 验证文件
            if not ImageClassifier.is_supported_format(file.filename):
                errors.append({
                    "filename": file.filename,
                    "error": f"Unsupported file format"
                })
                continue

            # 读取文件数据
            file_data = await file.read()

            # 验证文件大小
            if not ImageClassifier.is_file_size_valid(len(file_data)):
                errors.append({
                    "filename": file.filename,
                    "error": f"File too large"
                })
                continue

            # 创建分类器
            classifier = ImageClassifier(model)

            # 分类图片
            result = await classifier.classify_image_data(file_data)

            results.append({
                "filename": file.filename,
                "category": result.category,
                "confidence": result.confidence,
                "reasoning": result.reasoning,
                "model_used": classifier.model_type
            })

        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })

    return JSONResponse({
        "results": results,
        "errors": errors
    })


@app.get("/categories")
async def get_categories():
    """获取所有可用的图片分类"""
    categories = config_manager.get_categories()
    return {
        "categories": {
            name: {
                "keywords": category.keywords,
                "description": category.description
            }
            for name, category in categories.items()
        }
    }


@app.get("/models")
async def get_available_models():
    """获取可用的模型列表"""
    return {
        "models": ModelFactory.get_available_models(),
        "default_model": config_manager.get_app_config().default_model
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "Image classifier is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)