"""
对话引擎模块

负责生成与Cursor交互的对话内容和指导策略
"""

import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger
from .ai_models import AIModelManager


class ConversationTemplate:
    """对话模板"""
    
    def __init__(self):
        self.templates = self._load_conversation_templates()
    
    def _load_conversation_templates(self) -> Dict[str, Dict[str, str]]:
        """加载对话模板"""
        return {
            "project_setup": {
                "initial_prompt": """
我需要创建一个{project_type}项目。

项目需求：
{requirement_summary}

技术栈：
{tech_stack}

请帮我：
1. 创建项目目录结构
2. 初始化项目配置
3. 安装必要的依赖

请逐步指导我完成项目初始化。
""",
                "follow_up_prompts": [
                    "项目结构看起来正确吗？有需要调整的地方吗？",
                    "依赖安装完成后，我们来配置开发环境",
                    "现在可以测试项目是否能正常启动"
                ]
            },
            "feature_implementation": {
                "initial_prompt": """
现在需要实现以下功能：

功能名称：{feature_name}
功能描述：{feature_description}
技术要求：{tech_requirements}

子任务包括：
{subtasks}

请指导我完成这个功能的开发，我们一步步来实现。
""",
                "follow_up_prompts": [
                    "这个实现看起来正确吗？有需要优化的地方吗？",
                    "我们需要添加错误处理和数据验证吗？",
                    "现在来编写测试用例验证功能",
                    "让我们测试一下这个功能是否工作正常"
                ]
            },
            "debugging": {
                "initial_prompt": """
在实现{feature_name}时遇到了问题：

错误信息：{error_message}
相关代码：{code_context}

请帮我分析和解决这个问题。
""",
                "follow_up_prompts": [
                    "这个解决方案有效吗？",
                    "还有其他潜在的问题需要注意吗？",
                    "让我们添加一些防护措施避免类似问题"
                ]
            },
            "code_review": {
                "initial_prompt": """
请帮我检查以下代码的质量：

文件：{file_path}
功能：{feature_description}

请关注：
1. 代码结构和可读性
2. 性能优化机会
3. 潜在的安全问题
4. 最佳实践建议
""",
                "follow_up_prompts": [
                    "根据你的建议，我来修改代码",
                    "这些修改是否符合最佳实践？",
                    "还有其他需要改进的地方吗？"
                ]
            },
            "testing": {
                "initial_prompt": """
现在需要为{feature_name}编写测试：

功能描述：{feature_description}
测试类型：{test_type}

请帮我：
1. 设计测试用例
2. 编写测试代码
3. 验证测试覆盖率
""",
                "follow_up_prompts": [
                    "测试用例是否覆盖了所有重要场景？",
                    "我们需要添加边界条件测试吗？",
                    "让我们运行测试看看结果"
                ]
            }
        }
    
    def get_conversation_template(self, task_type: str) -> Dict[str, str]:
        """获取对话模板"""
        return self.templates.get(task_type, self.templates["feature_implementation"])


class ConversationEngine:
    """对话引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化对话引擎"""
        self.config = config
        self.ai_manager = AIModelManager(config)
        self.template = ConversationTemplate()
        self.conversation_history = []
        logger.info("对话引擎已初始化")
    
    async def generate_initial_prompt(
        self, 
        task: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """生成初始对话提示"""
        
        task_type = self._determine_task_type(task)
        template = self.template.get_conversation_template(task_type)
        
        # 准备模板变量
        template_vars = await self._prepare_template_variables(task, context)
        
        # 生成初始提示
        initial_prompt = template["initial_prompt"].format(**template_vars)
        
        # 使用AI优化提示内容
        optimized_prompt = await self._optimize_prompt(initial_prompt, task, context)
        
        # 记录对话历史
        self.conversation_history.append({
            "type": "initial_prompt",
            "task_id": task.get("id"),
            "prompt": optimized_prompt,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        logger.info(f"为任务 {task.get('name')} 生成初始对话")
        return optimized_prompt
    
    def _determine_task_type(self, task: Dict[str, Any]) -> str:
        """确定任务类型"""
        task_type = task.get("type", "feature")
        
        type_mapping = {
            "setup": "project_setup",
            "feature": "feature_implementation", 
            "testing": "testing",
            "debug": "debugging",
            "review": "code_review"
        }
        
        return type_mapping.get(task_type, "feature_implementation")
    
    async def _prepare_template_variables(
        self, 
        task: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """准备模板变量"""
        
        # 从任务和上下文中提取信息
        variables = {
            "project_type": context.get("project_type", "web应用"),
            "requirement_summary": context.get("original_requirement", "未指定"),
            "feature_name": task.get("name", "未命名功能"),
            "feature_description": task.get("description", "无描述"),
            "tech_stack": self._format_tech_stack(context.get("tech_stack", {})),
            "subtasks": self._format_subtasks(task.get("subtasks", [])),
            "tech_requirements": self._extract_tech_requirements(task, context)
        }
        
        return variables
    
    def _format_tech_stack(self, tech_stack: Dict[str, Any]) -> str:
        """格式化技术栈信息"""
        if not tech_stack:
            return "待确定"
        
        formatted_lines = []
        for category, technologies in tech_stack.items():
            if isinstance(technologies, list):
                tech_list = ", ".join(technologies)
                formatted_lines.append(f"- {category}: {tech_list}")
            else:
                formatted_lines.append(f"- {category}: {technologies}")
        
        return "\n".join(formatted_lines)
    
    def _format_subtasks(self, subtasks: List[str]) -> str:
        """格式化子任务列表"""
        if not subtasks:
            return "无具体子任务"
        
        return "\n".join([f"- {subtask}" for subtask in subtasks])
    
    def _extract_tech_requirements(
        self, 
        task: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """提取技术要求"""
        requirements = []
        
        # 从任务类型推断要求
        task_type = task.get("type", "")
        if task_type == "frontend":
            requirements.append("响应式设计")
            requirements.append("现代化UI框架")
        elif task_type == "backend":
            requirements.append("RESTful API设计")
            requirements.append("数据库集成")
        elif task_type == "database":
            requirements.append("数据模型设计")
            requirements.append("索引优化")
        
        # 从复杂度推断要求
        complexity = context.get("complexity", "medium")
        if complexity == "high":
            requirements.append("性能优化")
            requirements.append("可扩展性设计")
        
        return ", ".join(requirements) if requirements else "基本功能实现"
    
    async def _optimize_prompt(
        self, 
        initial_prompt: str, 
        task: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """使用AI优化对话提示"""
        
        try:
            optimization_prompt = f"""
请优化以下对话提示，使其更加清晰、具体和实用：

原始提示：
{initial_prompt}

任务信息：
- 任务名称：{task.get('name')}
- 任务类型：{task.get('type')}
- 优先级：{task.get('priority')}

要求：
1. 保持核心意图不变
2. 增加具体的技术细节
3. 使指导更加明确
4. 确保分步骤执行
5. 语言简洁专业

请返回优化后的提示内容：
"""
            
            optimized = await self.ai_manager.generate_response(optimization_prompt)
            return optimized.strip()
            
        except Exception as e:
            logger.warning(f"提示优化失败，使用原始提示: {e}")
            return initial_prompt
    
    async def generate_follow_up_prompt(
        self, 
        task: Dict[str, Any], 
        progress_info: Dict[str, Any],
        issue_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """生成跟进对话提示"""
        
        task_type = self._determine_task_type(task)
        template = self.template.get_conversation_template(task_type)
        
        # 根据进度和问题生成跟进提示
        if issue_context:
            # 有问题需要解决
            follow_up = await self._generate_problem_solving_prompt(task, issue_context)
        else:
            # 正常进度跟进
            progress_stage = self._determine_progress_stage(progress_info)
            follow_up_templates = template.get("follow_up_prompts", [])
            
            if progress_stage < len(follow_up_templates):
                follow_up = follow_up_templates[progress_stage]
            else:
                follow_up = await self._generate_dynamic_follow_up(task, progress_info)
        
        # 记录对话历史
        self.conversation_history.append({
            "type": "follow_up",
            "task_id": task.get("id"),
            "prompt": follow_up,
            "progress_info": progress_info,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        logger.info(f"为任务 {task.get('name')} 生成跟进对话")
        return follow_up
    
    def _determine_progress_stage(self, progress_info: Dict[str, Any]) -> int:
        """确定进度阶段"""
        progress = progress_info.get("progress", 0)
        
        if progress < 25:
            return 0  # 初始阶段
        elif progress < 50:
            return 1  # 开发阶段
        elif progress < 75:
            return 2  # 测试阶段
        else:
            return 3  # 完成阶段
    
    async def _generate_problem_solving_prompt(
        self, 
        task: Dict[str, Any], 
        issue_context: Dict[str, Any]
    ) -> str:
        """生成问题解决提示"""
        
        issue_type = issue_context.get("type", "unknown")
        error_message = issue_context.get("error", "未知错误")
        
        problem_prompt = f"""
在执行任务 "{task.get('name')}" 时遇到了问题：

问题类型：{issue_type}
错误信息：{error_message}

请帮我分析和解决这个问题。需要：
1. 分析问题的可能原因
2. 提供解决方案
3. 给出预防措施

我们一步步来解决这个问题。
"""
        
        return problem_prompt
    
    async def _generate_dynamic_follow_up(
        self, 
        task: Dict[str, Any], 
        progress_info: Dict[str, Any]
    ) -> str:
        """动态生成跟进提示"""
        
        try:
            dynamic_prompt = f"""
请为以下开发任务生成一个合适的跟进问题：

任务：{task.get('name')}
描述：{task.get('description')}
当前进度：{progress_info.get('progress', 0)}%
已完成的子任务：{progress_info.get('completed_subtasks', [])}

请生成一个简洁的跟进问题，帮助推进任务进展。
"""
            
            response = await self.ai_manager.generate_response(dynamic_prompt)
            return response.strip()
            
        except Exception as e:
            logger.warning(f"动态跟进生成失败: {e}")
            return "当前进展如何？还需要什么帮助吗？"
    
    async def generate_completion_prompt(self, task: Dict[str, Any]) -> str:
        """生成任务完成确认提示"""
        
        completion_prompt = f"""
任务 "{task.get('name')}" 看起来已经完成了！

让我们来确认一下：
1. 所有功能都正常工作吗？
2. 代码质量符合标准吗？
3. 有需要进一步优化的地方吗？
4. 相关文档已经更新了吗？

如果一切正常，我们就可以继续下一个任务了。
"""
        
        # 记录完成对话
        self.conversation_history.append({
            "type": "completion",
            "task_id": task.get("id"),
            "prompt": completion_prompt,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        return completion_prompt
    
    def get_conversation_history(self, task_id: str = None) -> List[Dict[str, Any]]:
        """获取对话历史"""
        if task_id:
            return [entry for entry in self.conversation_history if entry.get("task_id") == task_id]
        return self.conversation_history
    
    def clear_history(self, task_id: str = None):
        """清理对话历史"""
        if task_id:
            self.conversation_history = [
                entry for entry in self.conversation_history 
                if entry.get("task_id") != task_id
            ]
        else:
            self.conversation_history = []
        
        logger.info(f"对话历史已清理{'(任务: ' + task_id + ')' if task_id else ''}")
    
    async def analyze_response_quality(self, response: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """分析Cursor响应质量"""
        
        try:
            analysis_prompt = f"""
请分析以下Cursor的响应质量：

任务：{task.get('name')}
响应内容：{response}

请评估：
1. 响应是否解决了问题 (1-5分)
2. 技术建议是否合理 (1-5分)  
3. 代码质量如何 (1-5分)
4. 是否需要进一步跟进 (是/否)

返回JSON格式：
{
  "problem_solved": 4,
  "technical_quality": 4,
  "code_quality": 4,
  "needs_followup": false,
  "summary": "响应质量总结"
}
"""
            
            analysis_text = await self.ai_manager.generate_response(analysis_prompt)
            
            # 尝试解析JSON
            import json
            import re
            
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group(0))
            else:
                # 默认分析结果
                analysis_result = {
                    "problem_solved": 3,
                    "technical_quality": 3,
                    "code_quality": 3,
                    "needs_followup": True,
                    "summary": "需要人工评估"
                }
            
            return analysis_result
            
        except Exception as e:
            logger.warning(f"响应质量分析失败: {e}")
            return {
                "problem_solved": 3,
                "technical_quality": 3,
                "code_quality": 3,
                "needs_followup": True,
                "summary": "分析失败，建议人工检查"
            }
