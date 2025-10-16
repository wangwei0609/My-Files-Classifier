#!/usr/bin/env python3
"""测试脚本示例"""

import sys
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services import ImageClassifier
from src.utils.config import config_manager


async def test_config():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    try:
        categories = config_manager.get_categories()
        print(f"✅ 加载了 {len(categories)} 个分类:")
        for name, category in categories.items():
            print(f"   - {name}: {category.description}")

        app_config = config_manager.get_app_config()
        print(f"✅ 应用配置: 默认模型={app_config.default_model}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


async def test_classifier():
    """测试分类器（不调用API）"""
    print("\n🤖 测试分类器初始化...")
    try:
        # 创建分类器实例
        classifier = ImageClassifier("openai")
        print("✅ 分类器初始化成功")

        # 测试配置方法
        formats = classifier.get_supported_formats()
        print(f"✅ 支持的格式: {formats}")

        max_size = classifier.get_max_file_size()
        print(f"✅ 最大文件大小: {max_size}MB")

        return True
    except Exception as e:
        print(f"❌ 分类器测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🧪 图片分类器测试")
    print("=" * 50)

    tests = [
        test_config,
        test_classifier,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if await test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n📝 下一步:")
        print("1. 配置 .env 文件中的API密钥")
        print("2. 运行 python run.py 启动服务")
        print("3. 访问 http://localhost:8000 使用Web界面")
    else:
        print("⚠️  部分测试失败，请检查配置。")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())