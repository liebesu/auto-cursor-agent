"""
Cursor交互接口模块

负责与Cursor进行自动化交互，执行开发任务
"""

import asyncio
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger
from .conversation_engine import ConversationEngine

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class CursorInterface:
    """Cursor交互接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化Cursor接口"""
        self.config = config
        self.cursor_config = config.get('cursor', {})
        self.conversation_engine = ConversationEngine(config)
        
        # 交互模式配置
        self.interaction_mode = self.cursor_config.get('interaction_mode', 'file_based')  # file_based, ui_automation, api
        self.cursor_executable = self.cursor_config.get('executable_path', '/Applications/Cursor.app/Contents/MacOS/Cursor')
        self.wait_timeout = self.cursor_config.get('wait_timeout', 30)
        
        # 初始化交互驱动
        self.driver = None
        self.playwright_context = None
        
        logger.info(f"Cursor交互接口已初始化 (模式: {self.interaction_mode})")
    
    async def execute_task(self, task: Dict[str, Any], workspace_path: str) -> Dict[str, Any]:
        """执行开发任务"""
        logger.info(f"正在执行任务: {task.get('name', 'Unknown')}")
        
        start_time = time.time()
        result = {
            "task_id": task.get('id'),
            "status": "in_progress",
            "files_created": [],
            "files_modified": [],
            "execution_time": 0,
            "conversation_log": [],
            "errors": []
        }
        
        try:
            # 1. 准备工作空间
            await self._prepare_workspace(workspace_path)
            
            # 2. 启动Cursor交互
            if self.interaction_mode == 'ui_automation':
                await self._execute_via_ui_automation(task, workspace_path, result)
            elif self.interaction_mode == 'file_based':
                await self._execute_via_file_based(task, workspace_path, result)
            else:
                # 默认使用文件交互模式
                await self._execute_via_file_based(task, workspace_path, result)
            
            # 3. 验证执行结果
            await self._verify_task_completion(task, workspace_path, result)
            
            result["status"] = "completed"
            execution_time = time.time() - start_time
            result["execution_time"] = round(execution_time, 2)
            
            logger.success(f"任务执行完成: {task.get('name')} (耗时: {execution_time:.1f}秒)")
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            result["status"] = "failed"
            result["errors"].append(str(e))
            result["execution_time"] = round(time.time() - start_time, 2)
        
        return result
    
    async def _prepare_workspace(self, workspace_path: str):
        """准备工作空间"""
        workspace = Path(workspace_path)
        if not workspace.exists():
            workspace.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建工作空间: {workspace_path}")
        
        # 确保基本目录结构存在
        essential_dirs = ['src', 'logs', 'temp']
        for dir_name in essential_dirs:
            (workspace / dir_name).mkdir(exist_ok=True)
    
    async def _execute_via_file_based(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        result: Dict[str, Any]
    ):
        """通过文件交互方式执行任务"""
        
        # 1. 生成任务指导文件
        guidance_content = await self._generate_task_guidance(task, workspace_path)
        
        # 2. 创建任务文件
        task_file_path = await self._create_task_file(task, workspace_path, guidance_content)
        result["conversation_log"].append({
            "type": "task_file_created",
            "path": str(task_file_path),
            "content": guidance_content
        })
        
        # 3. 启动Cursor并打开工作空间
        cursor_process = await self._start_cursor(workspace_path)
        
        if cursor_process:
            # 4. 等待用户或自动化工具完成任务
            await self._monitor_task_progress(task, workspace_path, result)
            
            # 5. 清理进程
            try:
                cursor_process.terminate()
                await asyncio.sleep(1)
                if cursor_process.poll() is None:
                    cursor_process.kill()
            except:
                pass
    
    async def _execute_via_ui_automation(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        result: Dict[str, Any]
    ):
        """通过UI自动化方式执行任务"""
        
        if not SELENIUM_AVAILABLE and not PLAYWRIGHT_AVAILABLE:
            logger.warning("UI自动化库不可用，切换到文件交互模式")
            await self._execute_via_file_based(task, workspace_path, result)
            return
        
        try:
            # 启动Cursor
            await self._start_cursor(workspace_path)
            await asyncio.sleep(3)  # 等待Cursor启动
            
            # 使用Playwright进行UI自动化
            if PLAYWRIGHT_AVAILABLE:
                await self._execute_with_playwright(task, workspace_path, result)
            elif SELENIUM_AVAILABLE:
                await self._execute_with_selenium(task, workspace_path, result)
                
        except Exception as e:
            logger.error(f"UI自动化执行失败: {e}")
            # 回退到文件交互模式
            await self._execute_via_file_based(task, workspace_path, result)
    
    async def _generate_task_guidance(self, task: Dict[str, Any], workspace_path: str) -> str:
        """生成任务指导内容"""
        
        # 准备上下文信息
        context = {
            "workspace_path": workspace_path,
            "task": task
        }
        
        # 使用对话引擎生成指导内容
        guidance = await self.conversation_engine.generate_initial_prompt(task, context)
        
        # 添加项目特定信息
        project_info = await self._gather_project_info(workspace_path)
        
        full_guidance = f"""# 开发任务指导

## 任务信息
- **任务名称**: {task.get('name', '未知任务')}
- **任务描述**: {task.get('description', '无描述')}
- **任务类型**: {task.get('type', 'feature')}
- **优先级**: {task.get('priority', 3)}
- **预估时间**: {task.get('estimated_hours', 4)} 小时

## 项目环境
- **工作空间**: {workspace_path}
- **项目结构**: {project_info.get('structure', '标准结构')}
- **当前文件**: {len(project_info.get('files', []))} 个文件

## 开发指导

{guidance}

## 子任务清单
"""
        
        # 添加子任务
        subtasks = task.get('subtasks', [])
        if subtasks:
            for i, subtask in enumerate(subtasks, 1):
                full_guidance += f"{i}. [ ] {subtask}\n"
        else:
            full_guidance += "1. [ ] 开始实现功能\n2. [ ] 编写测试\n3. [ ] 文档更新\n"
        
        full_guidance += f"""

## 完成标准
- 所有子任务已完成
- 代码通过基本测试
- 符合项目代码规范
- 相关文档已更新

## 注意事项
- 遵循项目现有的代码风格
- 确保向后兼容性
- 添加适当的错误处理
- 考虑性能和安全性

---
*此文件由 Auto Cursor Agent 自动生成*
*如有疑问，请查看任务详情或联系开发团队*
"""
        
        return full_guidance
    
    async def _gather_project_info(self, workspace_path: str) -> Dict[str, Any]:
        """收集项目信息"""
        workspace = Path(workspace_path)
        
        info = {
            "structure": "未知",
            "files": [],
            "technologies": []
        }
        
        if not workspace.exists():
            return info
        
        # 收集文件信息
        try:
            files = []
            for file_path in workspace.rglob("*"):
                if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['.git', 'node_modules', '__pycache__']):
                    files.append(str(file_path.relative_to(workspace)))
            info["files"] = files[:20]  # 限制数量
            
            # 检测技术栈
            if (workspace / "package.json").exists():
                info["technologies"].append("Node.js")
            if (workspace / "requirements.txt").exists():
                info["technologies"].append("Python")
            if (workspace / "Cargo.toml").exists():
                info["technologies"].append("Rust")
            if (workspace / "go.mod").exists():
                info["technologies"].append("Go")
                
        except Exception as e:
            logger.warning(f"收集项目信息失败: {e}")
        
        return info
    
    async def _create_task_file(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        guidance_content: str
    ) -> Path:
        """创建任务指导文件"""
        
        workspace = Path(workspace_path)
        tasks_dir = workspace / "auto_cursor_tasks"
        tasks_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        task_id = task.get('id', 'unknown')
        task_name = task.get('name', 'unknown').replace(' ', '_').lower()
        filename = f"{task_id}_{task_name}.md"
        
        task_file = tasks_dir / filename
        
        # 写入文件
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(guidance_content)
        
        # 创建状态文件
        status_file = tasks_dir / f"{task_id}_status.json"
        status_data = {
            "task_id": task_id,
            "status": "created",
            "created_at": time.time(),
            "progress": 0,
            "completed_subtasks": []
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        logger.info(f"任务文件已创建: {task_file}")
        return task_file
    
    async def _start_cursor(self, workspace_path: str) -> Optional[subprocess.Popen]:
        """启动Cursor"""
        
        try:
            # 构建启动命令
            cursor_cmd = [self.cursor_executable, workspace_path]
            
            # 启动Cursor
            process = subprocess.Popen(
                cursor_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"Cursor已启动，PID: {process.pid}")
            return process
            
        except FileNotFoundError:
            logger.error(f"Cursor可执行文件未找到: {self.cursor_executable}")
            return None
        except Exception as e:
            logger.error(f"启动Cursor失败: {e}")
            return None
    
    async def _monitor_task_progress(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        result: Dict[str, Any]
    ):
        """监控任务进度"""
        
        task_id = task.get('id')
        workspace = Path(workspace_path)
        status_file = workspace / "auto_cursor_tasks" / f"{task_id}_status.json"
        
        monitor_duration = self.cursor_config.get('monitor_duration', 300)  # 5分钟
        check_interval = 10  # 每10秒检查一次
        
        start_time = time.time()
        
        while time.time() - start_time < monitor_duration:
            try:
                # 检查状态文件
                if status_file.exists():
                    with open(status_file, 'r', encoding='utf-8') as f:
                        status_data = json.load(f)
                    
                    if status_data.get('status') == 'completed':
                        logger.info(f"任务 {task_id} 已完成")
                        result["conversation_log"].append({
                            "type": "task_completed",
                            "timestamp": time.time(),
                            "status": status_data
                        })
                        break
                
                # 检查文件变化
                file_changes = await self._detect_file_changes(workspace_path)
                if file_changes:
                    result["files_modified"].extend(file_changes.get('modified', []))
                    result["files_created"].extend(file_changes.get('created', []))
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.warning(f"监控任务进度时出错: {e}")
                await asyncio.sleep(check_interval)
    
    async def _detect_file_changes(self, workspace_path: str) -> Dict[str, List[str]]:
        """检测文件变化"""
        # 这里可以实现文件监控逻辑
        # 简化版本：检查最近修改的文件
        
        workspace = Path(workspace_path)
        recent_files = {"modified": [], "created": []}
        
        try:
            current_time = time.time()
            
            for file_path in workspace.rglob("*"):
                if file_path.is_file():
                    # 检查最近1分钟内修改的文件
                    if current_time - file_path.stat().st_mtime < 60:
                        relative_path = str(file_path.relative_to(workspace))
                        
                        # 简单判断是新创建还是修改的文件
                        if current_time - file_path.stat().st_ctime < 60:
                            recent_files["created"].append(relative_path)
                        else:
                            recent_files["modified"].append(relative_path)
        
        except Exception as e:
            logger.warning(f"检测文件变化失败: {e}")
        
        return recent_files
    
    async def _verify_task_completion(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        result: Dict[str, Any]
    ):
        """验证任务完成情况"""
        
        task_id = task.get('id')
        workspace = Path(workspace_path)
        status_file = workspace / "auto_cursor_tasks" / f"{task_id}_status.json"
        
        # 检查状态文件
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                
                if status_data.get('status') == 'completed':
                    result["verification"] = {
                        "status_file_completed": True,
                        "progress": status_data.get('progress', 0),
                        "completed_subtasks": status_data.get('completed_subtasks', [])
                    }
                    return
            except Exception as e:
                logger.warning(f"读取状态文件失败: {e}")
        
        # 基于文件变化验证
        if result["files_created"] or result["files_modified"]:
            result["verification"] = {
                "status_file_completed": False,
                "files_changed": True,
                "created_count": len(result["files_created"]),
                "modified_count": len(result["files_modified"])
            }
        else:
            result["verification"] = {
                "status_file_completed": False,
                "files_changed": False,
                "warning": "没有检测到文件变化"
            }
    
    async def _execute_with_playwright(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        result: Dict[str, Any]
    ):
        """使用Playwright进行UI自动化"""
        # 这里可以实现Playwright自动化逻辑
        # 目前作为占位符
        logger.info("Playwright UI自动化功能待实现")
        pass
    
    async def _execute_with_selenium(
        self, 
        task: Dict[str, Any], 
        workspace_path: str, 
        result: Dict[str, Any]
    ):
        """使用Selenium进行UI自动化"""
        # 这里可以实现Selenium自动化逻辑
        # 目前作为占位符
        logger.info("Selenium UI自动化功能待实现")
        pass
    
    async def cleanup(self):
        """清理资源"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        if self.playwright_context:
            try:
                await self.playwright_context.close()
            except:
                pass
        
        logger.info("Cursor接口资源已清理")
