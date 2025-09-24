"""
任务模板模块

定义不同项目类型的标准任务模板
"""

from typing import Dict, List, Any


class TaskTemplate:
    """任务模板管理器"""
    
    def __init__(self):
        self.templates = self._load_task_templates()
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载任务模板"""
        return {
            "web_app": {
                "project_setup": {
                    "name": "项目初始化",
                    "description": "创建项目基础结构和配置",
                    "type": "setup",
                    "priority": 1,
                    "estimated_hours": 2,
                    "dependencies": [],
                    "subtasks": [
                        "创建项目目录结构",
                        "初始化包管理器配置",
                        "设置开发环境",
                        "配置版本控制"
                    ]
                },
                "frontend_setup": {
                    "name": "前端环境搭建", 
                    "description": "设置前端开发环境和基础组件",
                    "type": "frontend",
                    "priority": 2,
                    "estimated_hours": 4,
                    "dependencies": ["project_setup"],
                    "subtasks": [
                        "安装前端框架",
                        "配置路由系统", 
                        "设置样式框架",
                        "创建基础组件"
                    ]
                },
                "backend_setup": {
                    "name": "后端环境搭建",
                    "description": "设置后端服务和API框架", 
                    "type": "backend",
                    "priority": 2,
                    "estimated_hours": 4,
                    "dependencies": ["project_setup"],
                    "subtasks": [
                        "安装后端框架",
                        "配置数据库连接",
                        "设置API路由",
                        "实现基础中间件"
                    ]
                },
                "database_setup": {
                    "name": "数据库设计",
                    "description": "设计和实现数据模型",
                    "type": "database", 
                    "priority": 3,
                    "estimated_hours": 3,
                    "dependencies": ["backend_setup"],
                    "subtasks": [
                        "设计数据模型",
                        "创建数据库表",
                        "实现数据访问层",
                        "添加数据验证"
                    ]
                },
                "core_features": {
                    "name": "核心功能实现",
                    "description": "实现主要业务功能",
                    "type": "feature",
                    "priority": 5,
                    "estimated_hours": 12,
                    "dependencies": ["database_setup", "frontend_setup"],
                    "subtasks": []  # 根据具体需求动态生成
                },
                "testing": {
                    "name": "测试和质量保证",
                    "description": "编写测试用例和质量检查",
                    "type": "testing",
                    "priority": 7,
                    "estimated_hours": 6,
                    "dependencies": ["core_features"],
                    "subtasks": [
                        "单元测试编写",
                        "集成测试编写", 
                        "端到端测试",
                        "性能测试"
                    ]
                },
                "deployment": {
                    "name": "部署和发布",
                    "description": "配置生产环境和部署应用",
                    "type": "deployment",
                    "priority": 8,
                    "estimated_hours": 3,
                    "dependencies": ["testing"],
                    "subtasks": [
                        "配置生产环境",
                        "设置CI/CD流水线",
                        "部署到服务器", 
                        "配置监控和日志"
                    ]
                }
            },
            "mobile_app": {
                "project_setup": {
                    "name": "移动项目初始化",
                    "description": "创建移动应用项目结构",
                    "type": "setup",
                    "priority": 1,
                    "estimated_hours": 2,
                    "dependencies": [],
                    "subtasks": [
                        "创建React Native/Flutter项目",
                        "配置开发环境",
                        "设置模拟器",
                        "安装必要依赖"
                    ]
                },
                "navigation_setup": {
                    "name": "导航系统搭建",
                    "description": "实现应用导航和页面路由",
                    "type": "navigation",
                    "priority": 2,
                    "estimated_hours": 3,
                    "dependencies": ["project_setup"],
                    "subtasks": [
                        "配置导航库",
                        "设计页面结构",
                        "实现页面跳转",
                        "添加返回逻辑"
                    ]
                }
            },
            "data_analysis": {
                "project_setup": {
                    "name": "数据分析项目初始化",
                    "description": "创建数据分析项目环境", 
                    "type": "setup",
                    "priority": 1,
                    "estimated_hours": 1,
                    "dependencies": [],
                    "subtasks": [
                        "创建Python环境",
                        "安装分析库",
                        "设置Jupyter环境",
                        "准备数据目录"
                    ]
                },
                "data_collection": {
                    "name": "数据收集和预处理",
                    "description": "收集数据并进行清洗",
                    "type": "data",
                    "priority": 2,
                    "estimated_hours": 4,
                    "dependencies": ["project_setup"],
                    "subtasks": [
                        "数据源连接",
                        "数据收集",
                        "数据清洗",
                        "数据验证"
                    ]
                }
            }
        }
    
    def get_template_tasks(self, project_type: str) -> Dict[str, Dict[str, Any]]:
        """获取项目类型的任务模板"""
        return self.templates.get(project_type, self.templates["web_app"])
