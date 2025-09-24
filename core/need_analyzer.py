"""
需求分析器模块

负责将用户的模糊需求转换为具体的技术需求和开发任务
"""

import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger
from .ai_models import AIModelManager


class RequirementProcessor:
    """需求处理器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载需求分析模板"""
        return {
            "web_app": {
                "keywords": ["网站", "web", "网页", "前端", "后端", "全栈"],
                "default_tech_stack": {
                    "frontend": ["React", "Vue.js", "Next.js"],
                    "backend": ["Node.js", "Express", "FastAPI"],
                    "database": ["PostgreSQL", "MongoDB"],
                    "deployment": ["Vercel", "Docker", "AWS"]
                }
            },
            "mobile_app": {
                "keywords": ["app", "移动", "手机", "ios", "android", "flutter"],
                "default_tech_stack": {
                    "framework": ["React Native", "Flutter", "Swift/Kotlin"],
                    "backend": ["Node.js", "Python", "Firebase"],
                    "database": ["SQLite", "Firebase", "Supabase"]
                }
            },
            "data_analysis": {
                "keywords": ["数据", "分析", "图表", "统计", "pandas", "可视化"],
                "default_tech_stack": {
                    "language": ["Python", "R"],
                    "frameworks": ["Pandas", "NumPy", "Matplotlib", "Streamlit"],
                    "tools": ["Jupyter", "Plotly", "Seaborn"]
                }
            },
            "api_service": {
                "keywords": ["api", "接口", "服务", "后端", "restful", "graphql"],
                "default_tech_stack": {
                    "framework": ["FastAPI", "Express", "Django"],
                    "database": ["PostgreSQL", "Redis"],
                    "tools": ["Docker", "Swagger", "Postman"]
                }
            }
        }
    
    def detect_project_type(self, requirement: str) -> str:
        """检测项目类型"""
        requirement_lower = requirement.lower()
        
        for project_type, template in self.templates.items():
            for keyword in template["keywords"]:
                if keyword in requirement_lower:
                    return project_type
        
        return "general"
    
    def extract_features(self, analyzed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取和标准化功能特性"""
        features = analyzed_data.get("features", [])
        standardized_features = []
        
        for feature in features:
            if isinstance(feature, str):
                # 如果是字符串，转换为标准格式
                standardized_features.append({
                    "name": feature,
                    "description": "",
                    "priority": 3,
                    "estimated_hours": 4
                })
            elif isinstance(feature, dict):
                # 确保所有必需字段存在
                standardized_features.append({
                    "name": feature.get("name", "Unknown Feature"),
                    "description": feature.get("description", ""),
                    "priority": feature.get("priority", 3),
                    "estimated_hours": feature.get("estimated_hours", 4)
                })
        
        return standardized_features
    
    def validate_tech_stack(self, tech_stack: Dict[str, Any], project_type: str) -> Dict[str, Any]:
        """验证和完善技术栈"""
        if not tech_stack or not isinstance(tech_stack, dict):
            # 如果没有技术栈，使用默认模板
            if project_type in self.templates:
                return self.templates[project_type]["default_tech_stack"]
            else:
                return {
                    "frontend": ["React"],
                    "backend": ["Node.js"],
                    "database": ["PostgreSQL"]
                }
        
        return tech_stack


class NeedAnalyzer:
    """需求分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化需求分析器"""
        self.config = config
        self.ai_manager = AIModelManager(config)
        self.processor = RequirementProcessor()
        logger.info("需求分析器已初始化")
    
    async def analyze(self, requirement: str) -> Dict[str, Any]:
        """分析用户需求"""
        logger.info(f"正在分析需求: {requirement}")
        
        try:
            # 1. 检测项目类型
            project_type = self.processor.detect_project_type(requirement)
            logger.info(f"检测到项目类型: {project_type}")
            
            # 2. 使用AI模型进行深度分析
            ai_analysis = await self.ai_manager.analyze_requirement(requirement)
            
            # 3. 处理和标准化分析结果
            processed_result = await self._process_analysis_result(
                requirement, ai_analysis, project_type
            )
            
            # 4. 生成最终的分析报告
            final_result = await self._generate_analysis_report(processed_result)
            
            logger.success("需求分析完成")
            return final_result
            
        except Exception as e:
            logger.error(f"需求分析失败: {e}")
            # 返回基础的分析结果
            return await self._generate_fallback_analysis(requirement)
    
    async def _process_analysis_result(
        self, 
        requirement: str, 
        ai_analysis: Dict[str, Any], 
        project_type: str
    ) -> Dict[str, Any]:
        """处理AI分析结果"""
        
        # 提取和标准化功能特性
        features = self.processor.extract_features(ai_analysis)
        
        # 验证技术栈
        tech_stack = self.processor.validate_tech_stack(
            ai_analysis.get("tech_stack", {}), project_type
        )
        
        # 处理项目结构
        project_structure = ai_analysis.get("project_structure", {})
        if not project_structure:
            project_structure = await self._generate_default_structure(project_type)
        
        return {
            "original_requirement": requirement,
            "project_type": project_type,
            "features": features,
            "tech_stack": tech_stack,
            "project_structure": project_structure,
            "complexity": ai_analysis.get("complexity", "medium"),
            "estimated_hours": ai_analysis.get("estimated_hours", 40),
            "dependencies": ai_analysis.get("dependencies", []),
            "milestones": ai_analysis.get("milestones", []),
            "risks": ai_analysis.get("risks", []),
            "ai_analysis_raw": ai_analysis
        }
    
    async def _generate_default_structure(self, project_type: str) -> Dict[str, Any]:
        """生成默认项目结构"""
        structures = {
            "web_app": {
                "src/": {
                    "components/": "React组件",
                    "pages/": "页面文件",
                    "utils/": "工具函数",
                    "styles/": "样式文件"
                },
                "public/": "静态资源",
                "package.json": "依赖配置",
                "README.md": "项目说明"
            },
            "mobile_app": {
                "src/": {
                    "screens/": "页面屏幕",
                    "components/": "组件",
                    "navigation/": "导航配置",
                    "services/": "API服务"
                },
                "assets/": "资源文件",
                "package.json": "依赖配置"
            },
            "data_analysis": {
                "data/": "数据文件",
                "notebooks/": "Jupyter笔记本",
                "src/": {
                    "analysis/": "分析脚本",
                    "visualization/": "可视化代码",
                    "utils/": "工具函数"
                },
                "requirements.txt": "Python依赖"
            }
        }
        
        return structures.get(project_type, structures["web_app"])
    
    async def _generate_analysis_report(self, processed_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成完整的分析报告"""
        
        # 计算总体评估
        total_features = len(processed_result["features"])
        high_priority_features = len([f for f in processed_result["features"] if f["priority"] >= 4])
        
        processed_result.update({
            "analysis_summary": {
                "total_features": total_features,
                "high_priority_features": high_priority_features,
                "recommended_team_size": self._estimate_team_size(processed_result),
                "development_phases": self._suggest_development_phases(processed_result),
                "success_criteria": self._define_success_criteria(processed_result)
            },
            "next_steps": [
                "确认技术栈选择",
                "细化功能需求",
                "设计数据模型",
                "创建项目骨架",
                "实现核心功能"
            ]
        })
        
        return processed_result
    
    def _estimate_team_size(self, analysis: Dict[str, Any]) -> int:
        """估算团队规模"""
        complexity = analysis.get("complexity", "medium")
        estimated_hours = analysis.get("estimated_hours", 40)
        
        if complexity == "low" or estimated_hours < 40:
            return 1
        elif complexity == "medium" or estimated_hours < 160:
            return 2
        else:
            return 3
    
    def _suggest_development_phases(self, analysis: Dict[str, Any]) -> List[str]:
        """建议开发阶段"""
        phases = ["需求确认", "架构设计", "核心功能开发"]
        
        if len(analysis.get("features", [])) > 5:
            phases.append("功能集成")
        
        phases.extend(["测试验证", "部署上线"])
        return phases
    
    def _define_success_criteria(self, analysis: Dict[str, Any]) -> List[str]:
        """定义成功标准"""
        criteria = [
            "所有核心功能正常运行",
            "代码质量达到标准",
            "通过功能测试"
        ]
        
        if analysis.get("project_type") == "web_app":
            criteria.append("响应式设计兼容性")
        elif analysis.get("project_type") == "mobile_app":
            criteria.append("在主流设备上运行流畅")
        elif analysis.get("project_type") == "data_analysis":
            criteria.append("数据分析结果准确可靠")
        
        return criteria
    
    async def _generate_fallback_analysis(self, requirement: str) -> Dict[str, Any]:
        """生成备用分析结果（AI分析失败时使用）"""
        logger.warning("使用备用分析方案")
        
        project_type = self.processor.detect_project_type(requirement)
        
        return {
            "original_requirement": requirement,
            "project_type": project_type,
            "features": [
                {
                    "name": "基础功能实现",
                    "description": "根据需求实现基本功能",
                    "priority": 4,
                    "estimated_hours": 8
                }
            ],
            "tech_stack": self.processor.validate_tech_stack({}, project_type),
            "project_structure": await self._generate_default_structure(project_type),
            "complexity": "medium",
            "estimated_hours": 40,
            "dependencies": [],
            "milestones": ["项目初始化", "核心功能开发", "测试部署"],
            "risks": ["需求不够明确"],
            "analysis_summary": {
                "total_features": 1,
                "high_priority_features": 1,
                "recommended_team_size": 1,
                "development_phases": ["需求确认", "开发实现", "测试部署"],
                "success_criteria": ["功能正常运行", "代码质量合格"]
            },
            "next_steps": [
                "详细了解需求",
                "确认技术方案",
                "开始开发"
            ],
            "fallback_analysis": True
        }
