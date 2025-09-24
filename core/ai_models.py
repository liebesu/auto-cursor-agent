"""
AI模型集成模块

支持多种AI模型进行需求分析和代码生成
"""

import asyncio
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from loguru import logger

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


class BaseAIModel(ABC):
    """AI模型基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get('model', 'unknown')
        
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回复"""
        pass
    
    @abstractmethod
    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """分析需求"""
        pass


class OpenAIModel(BaseAIModel):
    """OpenAI GPT模型"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not openai:
            raise ImportError("请安装openai包: pip install openai")
        
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API密钥未配置")
        
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=config.get('base_url', 'https://api.openai.com/v1')
        )
        logger.info(f"OpenAI模型已初始化: {self.model_name}")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回复"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 4000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7))
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """分析需求"""
        prompt = f"""
作为一个专业的软件架构师和产品经理，请分析以下用户需求，并提供详细的技术分析。

用户需求：{requirement}

请以JSON格式返回分析结果，包含以下字段：
1. features: 核心功能列表，每个功能包含name、description、priority（1-5）
2. tech_stack: 推荐的技术栈，包含frontend、backend、database、tools
3. project_structure: 项目目录结构
4. complexity: 项目复杂度评估（low/medium/high）
5. estimated_hours: 预估开发时间（小时）
6. dependencies: 主要依赖和第三方服务
7. milestones: 开发里程碑，按阶段划分
8. risks: 潜在风险和挑战

请确保分析全面、实用，技术选择要考虑最佳实践和开发效率。
"""
        
        try:
            response = await self.generate_response(prompt)
            # 尝试提取JSON部分
            import json
            import re
            
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有代码块，尝试找到大括号包围的内容
                brace_match = re.search(r'\{.*\}', response, re.DOTALL)
                if brace_match:
                    json_str = brace_match.group(0)
                else:
                    json_str = response
            
            result = json.loads(json_str)
            logger.success("需求分析完成")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败，返回原始响应: {e}")
            return {
                "raw_response": response,
                "parse_error": str(e),
                "features": [],
                "tech_stack": {},
                "complexity": "medium"
            }
        except Exception as e:
            logger.error(f"需求分析失败: {e}")
            raise


class ClaudeModel(BaseAIModel):
    """Anthropic Claude模型"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not anthropic:
            raise ImportError("请安装anthropic包: pip install anthropic")
        
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("Claude API密钥未配置")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        logger.info(f"Claude模型已初始化: {self.model_name}")
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回复"""
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 4000)),
                temperature=kwargs.get('temperature', self.config.get('temperature', 0.7)),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            raise
    
    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """分析需求"""
        prompt = f"""
请作为专业的软件架构师分析以下用户需求：

{requirement}

请以JSON格式返回详细的技术分析，包括：
- features: 功能分解和优先级
- tech_stack: 技术栈建议
- project_structure: 项目结构
- complexity: 复杂度评估
- estimated_hours: 时间预估
- dependencies: 依赖分析
- milestones: 开发阶段
- risks: 风险评估

确保分析专业、全面、可执行。
"""
        
        try:
            response = await self.generate_response(prompt)
            import json
            import re
            
            # 提取JSON内容（与OpenAI模型相同的逻辑）
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                brace_match = re.search(r'\{.*\}', response, re.DOTALL)
                if brace_match:
                    json_str = brace_match.group(0)
                else:
                    json_str = response
            
            result = json.loads(json_str)
            logger.success("Claude需求分析完成")
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败，返回原始响应: {e}")
            return {
                "raw_response": response,
                "parse_error": str(e),
                "features": [],
                "tech_stack": {},
                "complexity": "medium"
            }
        except Exception as e:
            logger.error(f"Claude需求分析失败: {e}")
            raise


class AIModelFactory:
    """AI模型工厂"""
    
    @staticmethod
    def create_model(model_type: str, config: Dict[str, Any]) -> BaseAIModel:
        """创建AI模型实例"""
        model_type = model_type.lower()
        
        if model_type == 'openai':
            return OpenAIModel(config)
        elif model_type == 'claude':
            return ClaudeModel(config)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    @staticmethod
    def get_available_models(config: Dict[str, Any]) -> List[str]:
        """获取可用的模型列表"""
        available = []
        
        ai_models_config = config.get('ai_models', {})
        
        for model_type in ['openai', 'claude']:
            model_config = ai_models_config.get(model_type, {})
            if model_config.get('api_key'):
                available.append(model_type)
        
        return available


class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.primary_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化可用的模型"""
        ai_models_config = self.config.get('ai_models', {})
        available_models = AIModelFactory.get_available_models(self.config)
        
        for model_type in available_models:
            try:
                model_config = ai_models_config[model_type]
                model = AIModelFactory.create_model(model_type, model_config)
                self.models[model_type] = model
                
                # 设置主要模型（优先OpenAI，然后Claude）
                if not self.primary_model:
                    if model_type == 'openai':
                        self.primary_model = model
                    elif model_type == 'claude' and not self.primary_model:
                        self.primary_model = model
                        
            except Exception as e:
                logger.warning(f"初始化{model_type}模型失败: {e}")
        
        if not self.primary_model:
            raise ValueError("没有可用的AI模型，请检查配置")
        
        logger.info(f"AI模型管理器已初始化，主要模型: {type(self.primary_model).__name__}")
    
    async def analyze_requirement(self, requirement: str, model_type: str = None) -> Dict[str, Any]:
        """使用指定模型分析需求"""
        if model_type:
            if model_type not in self.models:
                raise ValueError(f"模型 {model_type} 不可用")
            model = self.models[model_type]
        else:
            model = self.primary_model
        
        logger.info(f"使用 {type(model).__name__} 分析需求")
        return await model.analyze_requirement(requirement)
    
    async def generate_response(self, prompt: str, model_type: str = None, **kwargs) -> str:
        """生成回复"""
        if model_type:
            if model_type not in self.models:
                raise ValueError(f"模型 {model_type} 不可用")
            model = self.models[model_type]
        else:
            model = self.primary_model
        
        return await model.generate_response(prompt, **kwargs)
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.models.keys())

