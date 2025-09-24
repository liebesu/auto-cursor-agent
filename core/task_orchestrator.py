"""
任务编排器模块

负责管理开发任务的执行顺序和依赖关系
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from .ai_models import AIModelManager
from .task_templates import TaskTemplate
from .dependency_resolver import DependencyResolver


class TaskOrchestrator:
    """任务编排器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化任务编排器"""
        self.config = config
        self.ai_manager = AIModelManager(config)
        self.template = TaskTemplate()
        self.dependency_resolver = DependencyResolver()
        logger.info("任务编排器已初始化")
    
    async def decompose_tasks(self, analyzed_requirement: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分解任务"""
        logger.info("正在分解开发任务")
        
        try:
            # 1. 获取项目类型和基础任务模板
            project_type = analyzed_requirement.get("project_type", "web_app")
            template_tasks = self.template.get_template_tasks(project_type)
            
            # 2. 根据需求特性生成自定义任务
            custom_tasks = await self._generate_custom_tasks(analyzed_requirement)
            
            # 3. 合并模板任务和自定义任务
            all_tasks = await self._merge_tasks(template_tasks, custom_tasks, analyzed_requirement)
            
            # 4. 解析依赖关系并排序
            ordered_tasks = self._resolve_dependencies(all_tasks)
            
            # 5. 估算时间和优化任务
            optimized_tasks = await self._optimize_tasks(ordered_tasks, analyzed_requirement)
            
            logger.success(f"任务分解完成，共生成 {len(optimized_tasks)} 个任务")
            return optimized_tasks
            
        except Exception as e:
            logger.error(f"任务分解失败: {e}")
            # 返回基础任务列表
            return await self._generate_fallback_tasks(analyzed_requirement)
    
    async def _generate_custom_tasks(self, analyzed_requirement: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据需求生成自定义任务"""
        features = analyzed_requirement.get("features", [])
        custom_tasks = []
        
        for i, feature in enumerate(features):
            if isinstance(feature, dict):
                task_id = f"feature_{i+1}_{feature.get('name', 'unknown').lower().replace(' ', '_')}"
                custom_task = {
                    "id": task_id,
                    "name": f"实现功能: {feature.get('name', '未知功能')}",
                    "description": feature.get("description", ""),
                    "type": "feature",
                    "priority": feature.get("priority", 3) + 3,  # 在基础任务之后
                    "estimated_hours": feature.get("estimated_hours", 4),
                    "dependencies": ["database_setup", "frontend_setup"],  # 默认依赖
                    "subtasks": await self._generate_feature_subtasks(feature),
                    "feature_data": feature
                }
                custom_tasks.append(custom_task)
        
        return custom_tasks
    
    async def _generate_feature_subtasks(self, feature: Dict[str, Any]) -> List[str]:
        """为功能生成子任务"""
        feature_name = feature.get("name", "")
        feature_desc = feature.get("description", "")
        
        # 使用AI生成子任务
        try:
            prompt = f"""
为以下功能生成具体的开发子任务列表：

功能名称: {feature_name}
功能描述: {feature_desc}

请生成3-5个具体的开发步骤，每个步骤应该是具体可执行的任务。
返回格式：每行一个任务，不需要编号。

示例：
设计数据模型
实现后端API
创建前端组件
添加数据验证
编写单元测试
"""
            
            response = await self.ai_manager.generate_response(prompt)
            subtasks = [line.strip() for line in response.split('\n') if line.strip() and not line.strip().startswith('#')]
            return subtasks[:5]  # 最多5个子任务
            
        except Exception as e:
            logger.warning(f"AI生成子任务失败: {e}")
            return [
                f"设计{feature_name}数据结构",
                f"实现{feature_name}后端逻辑",
                f"创建{feature_name}前端界面",
                f"测试{feature_name}功能"
            ]
    
    async def _merge_tasks(
        self, 
        template_tasks: Dict[str, Dict[str, Any]], 
        custom_tasks: List[Dict[str, Any]], 
        analyzed_requirement: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """合并模板任务和自定义任务"""
        
        # 转换模板任务为列表格式
        template_task_list = []
        for task_id, task_data in template_tasks.items():
            task_data["id"] = task_id
            template_task_list.append(task_data)
        
        # 为自定义任务更新依赖关系
        updated_custom_tasks = []
        for task in custom_tasks:
            # 更新依赖关系，确保自定义任务依赖适当的基础任务
            if task["type"] == "feature":
                # 功能任务通常依赖数据库和前端设置
                base_deps = ["database_setup", "frontend_setup"]
                existing_deps = task.get("dependencies", [])
                # 只添加存在的依赖
                task["dependencies"] = [dep for dep in base_deps if dep in template_tasks] + existing_deps
            
            updated_custom_tasks.append(task)
        
        # 更新核心功能任务的子任务
        for task in template_task_list:
            if task["id"] == "core_features" and updated_custom_tasks:
                # 将自定义功能作为核心功能的子任务
                task["subtasks"] = [f"实现{ct['name']}" for ct in updated_custom_tasks]
                task["estimated_hours"] = sum(ct.get("estimated_hours", 4) for ct in updated_custom_tasks)
        
        # 合并所有任务
        all_tasks = template_task_list + updated_custom_tasks
        return all_tasks
    
    def _resolve_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析依赖关系并排序"""
        
        # 验证依赖关系
        validation_result = self.dependency_resolver.validate_dependencies(tasks)
        if not validation_result["valid"]:
            logger.warning(f"任务依赖关系验证失败: {validation_result}")
            # 清理无效依赖
            for task in tasks:
                valid_deps = []
                for dep in task.get("dependencies", []):
                    if any(t["id"] == dep for t in tasks):
                        valid_deps.append(dep)
                task["dependencies"] = valid_deps
        
        # 拓扑排序
        try:
            ordered_tasks = self.dependency_resolver.topological_sort(tasks)
            logger.info("任务依赖关系解析完成")
            return ordered_tasks
        except Exception as e:
            logger.error(f"依赖解析失败: {e}")
            # 按优先级排序作为备用方案
            return sorted(tasks, key=lambda x: x.get("priority", 5))
    
    async def _optimize_tasks(
        self, 
        tasks: List[Dict[str, Any]], 
        analyzed_requirement: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """优化任务列表"""
        
        # 根据复杂度调整时间估算
        complexity = analyzed_requirement.get("complexity", "medium")
        complexity_multiplier = {"low": 0.8, "medium": 1.0, "high": 1.3}.get(complexity, 1.0)
        
        optimized_tasks = []
        for i, task in enumerate(tasks):
            optimized_task = task.copy()
            
            # 调整时间估算
            optimized_task["estimated_hours"] = int(task.get("estimated_hours", 4) * complexity_multiplier)
            
            # 添加执行顺序
            optimized_task["execution_order"] = i + 1
            
            # 添加预计开始和结束时间
            if i == 0:
                optimized_task["estimated_start"] = datetime.now()
            else:
                prev_task = optimized_tasks[i-1]
                optimized_task["estimated_start"] = prev_task["estimated_end"]
            
            optimized_task["estimated_end"] = optimized_task["estimated_start"] + timedelta(
                hours=optimized_task["estimated_hours"]
            )
            
            # 添加任务状态
            optimized_task["status"] = "pending"
            optimized_task["progress"] = 0
            
            optimized_tasks.append(optimized_task)
        
        return optimized_tasks
    
    async def _generate_fallback_tasks(self, analyzed_requirement: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成备用任务列表"""
        logger.warning("使用备用任务生成方案")
        
        return [
            {
                "id": "project_setup",
                "name": "项目初始化",
                "description": "创建项目基础结构",
                "type": "setup",
                "priority": 1,
                "estimated_hours": 2,
                "dependencies": [],
                "subtasks": ["创建项目目录", "初始化配置文件"],
                "execution_order": 1,
                "estimated_start": datetime.now(),
                "estimated_end": datetime.now() + timedelta(hours=2),
                "status": "pending",
                "progress": 0
            },
            {
                "id": "core_development",
                "name": "核心功能开发",
                "description": "实现主要功能",
                "type": "feature",
                "priority": 2,
                "estimated_hours": 8,
                "dependencies": ["project_setup"],
                "subtasks": ["分析需求", "编写代码", "测试功能"],
                "execution_order": 2,
                "estimated_start": datetime.now() + timedelta(hours=2),
                "estimated_end": datetime.now() + timedelta(hours=10),
                "status": "pending",
                "progress": 0
            }
        ]
    
    def get_next_tasks(self, tasks: List[Dict[str, Any]], max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """获取下一批可执行的任务"""
        ready_tasks = []
        
        for task in tasks:
            if task["status"] == "pending":
                # 检查依赖是否完成
                dependencies_met = all(
                    any(t["id"] == dep and t["status"] == "completed" for t in tasks)
                    for dep in task.get("dependencies", [])
                )
                
                if dependencies_met:
                    ready_tasks.append(task)
                    if len(ready_tasks) >= max_concurrent:
                        break
        
        return ready_tasks
    
    def update_task_status(self, tasks: List[Dict[str, Any]], task_id: str, status: str, progress: int = None):
        """更新任务状态"""
        for task in tasks:
            if task["id"] == task_id:
                task["status"] = status
                if progress is not None:
                    task["progress"] = progress
                if status == "completed":
                    task["completed_at"] = datetime.now()
                elif status == "in_progress" and "started_at" not in task:
                    task["started_at"] = datetime.now()
                break
    
    def get_project_progress(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取项目整体进度"""
        if not tasks:
            return {"overall_progress": 0, "status": "not_started"}
        
        completed_tasks = len([t for t in tasks if t["status"] == "completed"])
        total_tasks = len(tasks)
        overall_progress = (completed_tasks / total_tasks) * 100
        
        in_progress_tasks = [t for t in tasks if t["status"] == "in_progress"]
        pending_tasks = [t for t in tasks if t["status"] == "pending"]
        
        if completed_tasks == total_tasks:
            status = "completed"
        elif in_progress_tasks:
            status = "in_progress"
        else:
            status = "pending"
        
        return {
            "overall_progress": round(overall_progress, 1),
            "status": status,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "in_progress_tasks": len(in_progress_tasks),
            "pending_tasks": len(pending_tasks)
        }
