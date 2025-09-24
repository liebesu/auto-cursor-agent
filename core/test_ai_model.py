"""
测试AI模型类 - 用于演示和测试
"""

import asyncio
from typing import Dict, Any
from loguru import logger


class TestAIModel:
    """测试用的AI模型类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = "test_model"
        logger.info("测试AI模型已初始化")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """生成测试响应"""
        await asyncio.sleep(0.1)  # 模拟API调用延迟
        return f"这是测试模式下对提示 '{prompt[:50]}...' 的响应"
    
    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """分析需求 - 测试版本"""
        await asyncio.sleep(0.1)  # 模拟AI分析时间
        
        # 根据关键词推测项目类型
        project_type = "web_app"
        if any(word in requirement.lower() for word in ["手机", "移动", "app", "android", "ios"]):
            project_type = "mobile_app"
        elif any(word in requirement.lower() for word in ["api", "接口", "服务"]):
            project_type = "api"
        elif any(word in requirement.lower() for word in ["数据", "分析", "统计"]):
            project_type = "data_analysis"
        
        # 提取功能特征
        features = []
        if "用户" in requirement:
            features.append("用户管理")
        if any(word in requirement for word in ["登录", "注册", "认证"]):
            features.append("用户认证")
        if any(word in requirement for word in ["存储", "数据库", "保存"]):
            features.append("数据存储")
        if any(word in requirement for word in ["界面", "UI", "前端"]):
            features.append("用户界面")
        if any(word in requirement for word in ["搜索", "查询"]):
            features.append("搜索功能")
        
        # 默认功能
        if not features:
            features = ["基本功能", "用户界面", "数据处理"]
        
        # 技术栈建议
        tech_stack = {
            "frontend": "React" if project_type == "web_app" else "React Native",
            "backend": "FastAPI",
            "database": "SQLite",
            "deployment": "Docker"
        }
        
        if project_type == "api":
            tech_stack["frontend"] = "无需前端"
        elif project_type == "data_analysis":
            tech_stack.update({
                "frontend": "Streamlit",
                "backend": "Python",
                "database": "pandas + CSV"
            })
        
        return {
            "project_type": project_type,
            "main_features": features,
            "tech_stack_suggestions": tech_stack,
            "complexity_level": "medium",
            "estimated_time": "2-3周",
            "key_challenges": ["架构设计", "用户体验优化"],
            "user_personas": ["普通用户", "管理员"],
            "success_criteria": ["功能完整", "性能良好", "用户体验友好"]
        }


class TestAIModelManager:
    """测试AI模型管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.test_model = TestAIModel(config)
        logger.info("测试AI模型管理器已初始化")
    
    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """分析需求"""
        return await self.test_model.analyze_requirement(requirement)
    
    async def generate_response(self, prompt: str, model_preference: str = "auto") -> Dict[str, Any]:
        """生成响应"""
        response_text = await self.test_model.generate_response(prompt)
        return {
            "content": response_text,
            "model": "test_model", 
            "tokens_used": len(prompt) + len(response_text),
            "success": True
        }
