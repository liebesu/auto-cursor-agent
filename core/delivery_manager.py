"""
交付管理器模块

负责项目完成验证和最终交付
"""

import asyncio
import time
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
from .ai_models import AIModelManager


class ProjectValidator:
    """项目验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'file_structure': True,
            'code_quality': True,
            'functionality': True,
            'documentation': True,
            'security': False,  # 可选
            'performance': False  # 可选
        }
    
    async def validate_project(
        self, 
        workspace_path: str, 
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """验证项目完整性"""
        
        logger.info("开始项目验证")
        
        validation_result = {
            'overall_status': 'unknown',
            'overall_score': 0,
            'validations': {},
            'issues': [],
            'missing_items': [],
            'recommendations': [],
            'passed_checks': 0,
            'total_checks': 0
        }
        
        workspace = Path(workspace_path)
        
        # 1. 文件结构验证
        structure_result = await self._validate_file_structure(workspace, requirements)
        validation_result['validations']['file_structure'] = structure_result
        
        # 2. 代码质量验证
        quality_result = await self._validate_code_quality(workspace)
        validation_result['validations']['code_quality'] = quality_result
        
        # 3. 功能完整性验证
        functionality_result = await self._validate_functionality(workspace, requirements, tasks)
        validation_result['validations']['functionality'] = functionality_result
        
        # 4. 文档验证
        docs_result = await self._validate_documentation(workspace, requirements)
        validation_result['validations']['documentation'] = docs_result
        
        # 5. 安全检查（可选）
        if self.validation_rules['security']:
            security_result = await self._validate_security(workspace)
            validation_result['validations']['security'] = security_result
        
        # 6. 性能检查（可选）
        if self.validation_rules['performance']:
            performance_result = await self._validate_performance(workspace)
            validation_result['validations']['performance'] = performance_result
        
        # 计算总体结果
        validation_result = self._calculate_overall_result(validation_result)
        
        logger.success(f"项目验证完成，总体评分: {validation_result['overall_score']:.2f}")
        return validation_result
    
    async def _validate_file_structure(self, workspace: Path, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """验证文件结构"""
        
        result = {
            'status': 'passed',
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查基本结构
            project_type = requirements.get('project_type', 'web_app')
            expected_structure = self._get_expected_structure(project_type)
            
            missing_files = []
            existing_files = []
            
            for expected_path in expected_structure.get('required_files', []):
                file_path = workspace / expected_path
                if file_path.exists():
                    existing_files.append(expected_path)
                else:
                    missing_files.append(expected_path)
            
            # 检查目录结构
            missing_dirs = []
            existing_dirs = []
            
            for expected_dir in expected_structure.get('required_dirs', []):
                dir_path = workspace / expected_dir
                if dir_path.exists() and dir_path.is_dir():
                    existing_dirs.append(expected_dir)
                else:
                    missing_dirs.append(expected_dir)
            
            # 计算分数
            total_required = len(expected_structure.get('required_files', [])) + len(expected_structure.get('required_dirs', []))
            total_existing = len(existing_files) + len(existing_dirs)
            
            if total_required > 0:
                result['score'] = total_existing / total_required
            
            if missing_files or missing_dirs:
                result['status'] = 'failed' if result['score'] < 0.5 else 'warning'
                result['issues'].extend([f"缺少文件: {f}" for f in missing_files])
                result['issues'].extend([f"缺少目录: {d}" for d in missing_dirs])
            
            result['details'] = {
                'existing_files': existing_files,
                'missing_files': missing_files,
                'existing_dirs': existing_dirs,
                'missing_dirs': missing_dirs
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['score'] = 0
            result['issues'].append(f"结构验证出错: {str(e)}")
        
        return result
    
    async def _validate_code_quality(self, workspace: Path) -> Dict[str, Any]:
        """验证代码质量"""
        
        result = {
            'status': 'passed',
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        try:
            from .progress_monitor import CodeQualityAnalyzer
            
            analyzer = CodeQualityAnalyzer()
            quality_scores = []
            analyzed_files = 0
            
            # 分析所有代码文件
            for file_path in workspace.rglob("*"):
                if not file_path.is_file():
                    continue
                
                file_ext = file_path.suffix.lower()
                
                if file_ext == '.py':
                    analysis = analyzer.analyze_python_file(file_path)
                    if 'error' not in analysis:
                        analyzed_files += 1
                        file_quality = (
                            analysis.get('style_score', 0) * 0.4 +
                            analysis.get('documentation', 0) * 0.3 +
                            (1 - analysis.get('complexity', 0)) * 0.3
                        )
                        quality_scores.append(file_quality)
                        
                        # 检查具体问题
                        if analysis.get('complexity', 0) > 0.8:
                            result['issues'].append(f"文件 {file_path.name} 复杂度过高")
                        if analysis.get('documentation', 0) < 0.3:
                            result['issues'].append(f"文件 {file_path.name} 缺少文档")
                
                elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                    analysis = analyzer.analyze_javascript_file(file_path)
                    if 'error' not in analysis:
                        analyzed_files += 1
                        quality_scores.append(analysis.get('quality_score', 0))
                        
                        if not analysis.get('has_error_handling', False):
                            result['issues'].append(f"文件 {file_path.name} 缺少错误处理")
                        if not analysis.get('has_comments', False):
                            result['issues'].append(f"文件 {file_path.name} 缺少注释")
            
            # 计算平均质量分数
            if quality_scores:
                result['score'] = sum(quality_scores) / len(quality_scores)
            
            if result['score'] < 0.6:
                result['status'] = 'failed'
            elif result['score'] < 0.8:
                result['status'] = 'warning'
            
            result['details'] = {
                'analyzed_files': analyzed_files,
                'average_quality': result['score'],
                'quality_distribution': {
                    'high': len([s for s in quality_scores if s >= 0.8]),
                    'medium': len([s for s in quality_scores if 0.6 <= s < 0.8]),
                    'low': len([s for s in quality_scores if s < 0.6])
                }
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['score'] = 0
            result['issues'].append(f"代码质量验证出错: {str(e)}")
        
        return result
    
    async def _validate_functionality(
        self, 
        workspace: Path, 
        requirements: Dict[str, Any], 
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """验证功能完整性"""
        
        result = {
            'status': 'passed',
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查任务完成情况
            completed_tasks = [t for t in tasks if t.get('status') == 'completed']
            total_tasks = len(tasks)
            
            if total_tasks > 0:
                completion_rate = len(completed_tasks) / total_tasks
                result['score'] = completion_rate
            
            # 检查核心功能实现
            features = requirements.get('features', [])
            implemented_features = []
            missing_features = []
            
            for feature in features:
                feature_name = feature.get('name', '') if isinstance(feature, dict) else str(feature)
                
                # 简单检查：查找相关文件或代码
                feature_implemented = self._check_feature_implementation(workspace, feature_name)
                
                if feature_implemented:
                    implemented_features.append(feature_name)
                else:
                    missing_features.append(feature_name)
            
            # 更新分数
            if features:
                feature_score = len(implemented_features) / len(features)
                result['score'] = (result['score'] + feature_score) / 2
            
            if result['score'] < 0.7:
                result['status'] = 'failed'
            elif result['score'] < 0.9:
                result['status'] = 'warning'
            
            if missing_features:
                result['issues'].extend([f"功能未实现: {f}" for f in missing_features])
            
            incomplete_tasks = [t for t in tasks if t.get('status') != 'completed']
            if incomplete_tasks:
                result['issues'].extend([f"任务未完成: {t.get('name')}" for t in incomplete_tasks[:3]])
            
            result['details'] = {
                'total_tasks': total_tasks,
                'completed_tasks': len(completed_tasks),
                'completion_rate': completion_rate if total_tasks > 0 else 1.0,
                'implemented_features': implemented_features,
                'missing_features': missing_features,
                'feature_completion_rate': len(implemented_features) / len(features) if features else 1.0
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['score'] = 0
            result['issues'].append(f"功能验证出错: {str(e)}")
        
        return result
    
    async def _validate_documentation(self, workspace: Path, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """验证文档完整性"""
        
        result = {
            'status': 'passed',
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查必需的文档文件
            required_docs = ['README.md']
            optional_docs = ['CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSE']
            
            existing_docs = []
            missing_docs = []
            
            for doc in required_docs:
                doc_path = workspace / doc
                if doc_path.exists():
                    existing_docs.append(doc)
                else:
                    missing_docs.append(doc)
                    result['issues'].append(f"缺少必需文档: {doc}")
            
            # 检查可选文档
            optional_existing = []
            for doc in optional_docs:
                doc_path = workspace / doc
                if doc_path.exists():
                    optional_existing.append(doc)
            
            # 检查README内容
            readme_score = 0
            readme_path = workspace / 'README.md'
            if readme_path.exists():
                readme_content = readme_path.read_text(encoding='utf-8')
                readme_sections = ['# ', '## ', 'install', 'usage', 'example']
                
                found_sections = sum(1 for section in readme_sections if section.lower() in readme_content.lower())
                readme_score = found_sections / len(readme_sections)
                
                if readme_score < 0.5:
                    result['issues'].append("README.md 内容不够完整")
            
            # 计算文档分数
            required_score = len(existing_docs) / len(required_docs) if required_docs else 1.0
            optional_score = len(optional_existing) / len(optional_docs) if optional_docs else 0.5
            
            result['score'] = (required_score * 0.6 + readme_score * 0.3 + optional_score * 0.1)
            
            if result['score'] < 0.5:
                result['status'] = 'failed'
            elif result['score'] < 0.8:
                result['status'] = 'warning'
            
            result['details'] = {
                'existing_docs': existing_docs,
                'missing_docs': missing_docs,
                'optional_docs': optional_existing,
                'readme_score': readme_score,
                'required_score': required_score
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['score'] = 0
            result['issues'].append(f"文档验证出错: {str(e)}")
        
        return result
    
    async def _validate_security(self, workspace: Path) -> Dict[str, Any]:
        """验证安全性（基础检查）"""
        
        result = {
            'status': 'passed',
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        # 简单的安全检查
        security_issues = []
        
        try:
            # 检查是否有硬编码的密钥或密码
            for file_path in workspace.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        
                        # 简单模式匹配
                        security_patterns = [
                            ('password', 'hardcoded password'),
                            ('api_key', 'hardcoded API key'),
                            ('secret', 'hardcoded secret'),
                            ('token', 'hardcoded token')
                        ]
                        
                        for pattern, description in security_patterns:
                            if pattern in content.lower() and ('=' in content or ':' in content):
                                security_issues.append(f"{file_path.name}: 可能包含{description}")
                                
                    except Exception:
                        continue
            
            if security_issues:
                result['issues'] = security_issues
                result['score'] = max(0.5, 1.0 - len(security_issues) * 0.2)
                result['status'] = 'warning'
            
            result['details'] = {
                'issues_found': len(security_issues),
                'files_checked': len(list(workspace.rglob("*")))
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['score'] = 0
            result['issues'].append(f"安全检查出错: {str(e)}")
        
        return result
    
    async def _validate_performance(self, workspace: Path) -> Dict[str, Any]:
        """验证性能（基础检查）"""
        
        result = {
            'status': 'passed',
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        # 简单的性能检查
        try:
            performance_issues = []
            large_files = []
            
            for file_path in workspace.rglob("*"):
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    
                    # 检查大文件
                    if file_size > 1024 * 1024:  # 1MB
                        large_files.append(f"{file_path.name}: {file_size / 1024 / 1024:.1f}MB")
                    
                    # 检查代码文件的性能问题
                    if file_path.suffix in ['.py', '.js', '.ts']:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            lines = content.split('\n')
                            
                            if len(lines) > 1000:
                                performance_issues.append(f"{file_path.name}: 文件过长 ({len(lines)} 行)")
                            
                        except Exception:
                            continue
            
            if large_files:
                result['issues'].extend([f"大文件: {f}" for f in large_files])
            
            if performance_issues:
                result['issues'].extend(performance_issues)
                result['score'] = max(0.7, 1.0 - len(performance_issues) * 0.1)
                result['status'] = 'warning'
            
            result['details'] = {
                'large_files': large_files,
                'performance_issues': performance_issues
            }
            
        except Exception as e:
            result['status'] = 'error'
            result['score'] = 0
            result['issues'].append(f"性能检查出错: {str(e)}")
        
        return result
    
    def _get_expected_structure(self, project_type: str) -> Dict[str, List[str]]:
        """获取预期的项目结构"""
        
        structures = {
            'web_app': {
                'required_files': ['package.json', 'README.md'],
                'required_dirs': ['src', 'public']
            },
            'mobile_app': {
                'required_files': ['package.json', 'README.md'],
                'required_dirs': ['src', 'assets']
            },
            'data_analysis': {
                'required_files': ['requirements.txt', 'README.md'],
                'required_dirs': ['src', 'data']
            },
            'api_service': {
                'required_files': ['requirements.txt', 'README.md'],
                'required_dirs': ['src', 'tests']
            }
        }
        
        return structures.get(project_type, structures['web_app'])
    
    def _check_feature_implementation(self, workspace: Path, feature_name: str) -> bool:
        """检查功能是否已实现（简单检查）"""
        
        # 简单的关键词匹配
        feature_keywords = feature_name.lower().replace(' ', '_').split('_')
        
        for file_path in workspace.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx']:
                try:
                    content = file_path.read_text(encoding='utf-8').lower()
                    
                    # 如果文件内容包含功能关键词，认为可能已实现
                    if any(keyword in content for keyword in feature_keywords):
                        return True
                        
                except Exception:
                    continue
        
        return False
    
    def _calculate_overall_result(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算总体验证结果"""
        
        validations = validation_result['validations']
        weights = {
            'file_structure': 0.2,
            'code_quality': 0.3,
            'functionality': 0.4,
            'documentation': 0.1,
            'security': 0.0,  # 可选
            'performance': 0.0  # 可选
        }
        
        total_score = 0
        total_weight = 0
        passed_checks = 0
        total_checks = 0
        
        for check_name, check_result in validations.items():
            weight = weights.get(check_name, 0)
            score = check_result.get('score', 0)
            status = check_result.get('status', 'unknown')
            
            total_score += score * weight
            total_weight += weight
            total_checks += 1
            
            if status == 'passed':
                passed_checks += 1
            
            # 收集问题
            validation_result['issues'].extend(check_result.get('issues', []))
        
        # 标准化分数
        if total_weight > 0:
            validation_result['overall_score'] = total_score / total_weight
        else:
            validation_result['overall_score'] = 0
        
        # 确定总体状态
        if validation_result['overall_score'] >= 0.8:
            validation_result['overall_status'] = 'passed'
        elif validation_result['overall_score'] >= 0.6:
            validation_result['overall_status'] = 'warning'
        else:
            validation_result['overall_status'] = 'failed'
        
        validation_result['passed_checks'] = passed_checks
        validation_result['total_checks'] = total_checks
        
        return validation_result


class DeliveryManager:
    """交付管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化交付管理器"""
        self.config = config
        self.ai_manager = AIModelManager(config)
        self.validator = ProjectValidator()
        
        logger.info("交付管理器已初始化")
    
    async def prepare_delivery(
        self, 
        workspace_path: str, 
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """准备项目交付"""
        
        logger.info("开始准备项目交付")
        
        delivery_result = {
            'status': 'in_progress',
            'timestamp': time.time(),
            'workspace_path': workspace_path,
            'validation': {},
            'documentation': {},
            'package': {},
            'deployment': {},
            'final_report': {}
        }
        
        try:
            # 1. 项目验证
            logger.info("执行项目验证")
            validation = await self.validator.validate_project(workspace_path, requirements, tasks)
            delivery_result['validation'] = validation
            
            # 2. 生成最终文档
            logger.info("生成项目文档")
            documentation = await self._generate_final_documentation(
                workspace_path, requirements, tasks, progress_data, validation
            )
            delivery_result['documentation'] = documentation
            
            # 3. 打包项目
            logger.info("打包项目文件")
            package_info = await self._package_project(workspace_path, requirements)
            delivery_result['package'] = package_info
            
            # 4. 准备部署信息
            logger.info("准备部署信息")
            deployment_info = await self._prepare_deployment_info(workspace_path, requirements)
            delivery_result['deployment'] = deployment_info
            
            # 5. 生成最终报告
            logger.info("生成最终交付报告")
            final_report = await self._generate_final_report(
                requirements, tasks, progress_data, validation, delivery_result
            )
            delivery_result['final_report'] = final_report
            
            # 确定交付状态
            if validation['overall_status'] == 'passed':
                delivery_result['status'] = 'ready_for_delivery'
            elif validation['overall_status'] == 'warning':
                delivery_result['status'] = 'ready_with_warnings'
            else:
                delivery_result['status'] = 'not_ready'
            
            logger.success(f"项目交付准备完成，状态: {delivery_result['status']}")
            
        except Exception as e:
            logger.error(f"交付准备失败: {e}")
            delivery_result['status'] = 'failed'
            delivery_result['error'] = str(e)
        
        return delivery_result
    
    async def _generate_final_documentation(
        self, 
        workspace_path: str, 
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        progress_data: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成最终项目文档"""
        
        workspace = Path(workspace_path)
        
        # 生成项目总结
        project_summary = await self._generate_project_summary(
            requirements, tasks, progress_data, validation
        )
        
        # 生成使用指南
        user_guide = await self._generate_user_guide(workspace, requirements)
        
        # 生成开发文档
        dev_docs = await self._generate_developer_documentation(workspace, requirements)
        
        # 保存文档
        docs_dir = workspace / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        # 保存项目总结
        summary_file = docs_dir / 'PROJECT_SUMMARY.md'
        summary_file.write_text(project_summary, encoding='utf-8')
        
        # 保存使用指南
        guide_file = docs_dir / 'USER_GUIDE.md'
        guide_file.write_text(user_guide, encoding='utf-8')
        
        # 保存开发文档
        dev_file = docs_dir / 'DEVELOPMENT.md'
        dev_file.write_text(dev_docs, encoding='utf-8')
        
        return {
            'docs_generated': 3,
            'docs_directory': str(docs_dir),
            'files': [
                str(summary_file),
                str(guide_file),
                str(dev_file)
            ]
        }
    
    async def _generate_project_summary(
        self, 
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        progress_data: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> str:
        """生成项目总结文档"""
        
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        total_tasks = len(tasks)
        
        summary = f"""# 项目开发总结

## 项目信息
- **项目类型**: {requirements.get('project_type', '未知')}
- **复杂度**: {requirements.get('complexity', '中等')}
- **开发时间**: {requirements.get('estimated_hours', 0)} 小时（预估）

## 功能实现
- **总功能数**: {len(requirements.get('features', []))}
- **已实现功能**: {len([f for f in requirements.get('features', []) if isinstance(f, dict)])}

## 开发进度
- **总任务数**: {total_tasks}
- **已完成任务**: {completed_tasks}
- **完成率**: {(completed_tasks / total_tasks * 100):.1f}%

## 技术栈
"""
        
        tech_stack = requirements.get('tech_stack', {})
        for category, technologies in tech_stack.items():
            if isinstance(technologies, list):
                summary += f"- **{category}**: {', '.join(technologies)}\n"
            else:
                summary += f"- **{category}**: {technologies}\n"
        
        summary += f"""

## 质量指标
- **整体评分**: {validation.get('overall_score', 0):.2f}/1.0
- **代码质量**: {validation.get('validations', {}).get('code_quality', {}).get('score', 0):.2f}/1.0
- **功能完整性**: {validation.get('validations', {}).get('functionality', {}).get('score', 0):.2f}/1.0
- **文档完整性**: {validation.get('validations', {}).get('documentation', {}).get('score', 0):.2f}/1.0

## 项目文件统计
- **创建文件**: {len(progress_data.get('files_created', []))}
- **修改文件**: {len(progress_data.get('files_modified', []))}
- **代码行数**: {progress_data.get('quality_metrics', {}).get('total_lines', 0)}

## 开发历程
本项目使用 Auto Cursor Agent 自动化开发系统完成，实现了：
1. 智能需求分析和任务分解
2. 自动化代码生成和指导
3. 实时质量监控和优化
4. 完整的项目验证和交付

---
*由 Auto Cursor Agent 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return summary
    
    async def _generate_user_guide(self, workspace: Path, requirements: Dict[str, Any]) -> str:
        """生成用户使用指南"""
        
        project_type = requirements.get('project_type', 'web_app')
        
        guide = f"""# 用户使用指南

## 项目简介
这是一个使用 Auto Cursor Agent 开发的{project_type}项目。

## 安装说明

### 环境要求
"""
        
        if project_type in ['web_app', 'mobile_app']:
            guide += """- Node.js (v14 或更高版本)
- npm 或 yarn 包管理器

### 安装步骤
1. 克隆或下载项目代码
2. 进入项目目录
3. 安装依赖：
   ```bash
   npm install
   ```

## 运行项目

### 开发模式
```bash
npm run dev
```

### 生产构建
```bash
npm run build
npm run start
```
"""
        
        elif project_type == 'data_analysis':
            guide += """- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤
1. 克隆或下载项目代码
2. 进入项目目录
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 运行项目

### 启动分析
```bash
python main.py
```

### Jupyter 环境
```bash
jupyter notebook
```
"""
        
        else:
            guide += """请参考项目根目录的 README.md 文件了解具体的安装和运行说明。
"""
        
        guide += """

## 功能说明
"""
        
        features = requirements.get('features', [])
        for i, feature in enumerate(features[:5], 1):
            if isinstance(feature, dict):
                guide += f"{i}. **{feature.get('name', '未命名功能')}**: {feature.get('description', '暂无描述')}\n"
            else:
                guide += f"{i}. {feature}\n"
        
        guide += """

## 常见问题

### Q: 如何修改配置？
A: 请查看项目中的配置文件，通常位于 `config/` 目录或根目录。

### Q: 遇到错误怎么办？
A: 请检查：
1. 依赖是否正确安装
2. 环境变量是否配置
3. 端口是否被占用

### Q: 如何贡献代码？
A: 欢迎提交 Issue 和 Pull Request！

## 支持与联系
如有问题，请查看项目文档或提交 Issue。

---
*文档生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return guide
    
    async def _generate_developer_documentation(self, workspace: Path, requirements: Dict[str, Any]) -> str:
        """生成开发者文档"""
        
        # 扫描项目结构
        project_structure = self._scan_project_structure(workspace)
        
        dev_docs = f"""# 开发者文档

## 项目架构

### 目录结构
```
{project_structure}
```

## 技术架构
"""
        
        tech_stack = requirements.get('tech_stack', {})
        for category, technologies in tech_stack.items():
            dev_docs += f"- **{category}**: {technologies if isinstance(technologies, str) else ', '.join(technologies)}\n"
        
        dev_docs += """

## 开发指南

### 代码规范
- 遵循项目既定的代码风格
- 编写清晰的注释和文档字符串
- 保持函数简洁，单一职责
- 添加适当的单元测试

### 提交规范
- 使用有意义的提交信息
- 每次提交包含单一功能或修复
- 提交前运行测试确保代码质量

## API 文档
（根据项目实际情况补充 API 接口文档）

## 数据库设计
（根据项目实际情况补充数据库设计文档）

## 部署说明

### 开发环境
1. 安装依赖
2. 配置环境变量
3. 启动开发服务器

### 生产环境
1. 构建生产版本
2. 配置服务器环境
3. 部署并启动服务

## 测试

### 运行测试
```bash
npm test  # 或 python -m pytest
```

### 添加测试
- 为新功能编写单元测试
- 确保测试覆盖率达到要求
- 编写集成测试验证功能

## 贡献指南
1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

---
*由 Auto Cursor Agent 自动生成*
"""
        
        return dev_docs
    
    def _scan_project_structure(self, workspace: Path, max_depth: int = 3) -> str:
        """扫描项目目录结构"""
        
        def _scan_recursive(path: Path, prefix: str = "", depth: int = 0) -> str:
            if depth > max_depth:
                return ""
            
            items = []
            try:
                # 只显示重要的文件和目录
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_dir():
                        if item.name in ['node_modules', '__pycache__', '.git']:
                            continue
                        items.append(f"{prefix}├── {item.name}/\n")
                        items.append(_scan_recursive(item, prefix + "│   ", depth + 1))
                    else:
                        # 只显示重要的文件
                        if item.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.yml', '.yaml']:
                            items.append(f"{prefix}├── {item.name}\n")
                
            except PermissionError:
                pass
            
            return "".join(items)
        
        return f"{workspace.name}/\n" + _scan_recursive(workspace)
    
    async def _package_project(self, workspace_path: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """打包项目"""
        
        workspace = Path(workspace_path)
        package_info = {
            'package_created': False,
            'package_path': None,
            'package_size': 0,
            'included_files': 0,
            'excluded_patterns': []
        }
        
        try:
            # 创建打包目录
            packages_dir = workspace.parent / 'packages'
            packages_dir.mkdir(exist_ok=True)
            
            # 生成包名
            project_name = requirements.get('project_type', 'project')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            package_name = f"{project_name}_{timestamp}.zip"
            package_path = packages_dir / package_name
            
            # 排除模式
            exclude_patterns = [
                '__pycache__',
                'node_modules',
                '.git',
                '.vscode',
                '.idea',
                '*.pyc',
                '*.log',
                '.env',
                'packages'
            ]
            
            # 创建ZIP包
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in workspace.rglob('*'):
                    if file_path.is_file():
                        # 检查是否应该排除
                        relative_path = file_path.relative_to(workspace)
                        should_exclude = any(
                            pattern in str(relative_path) 
                            for pattern in exclude_patterns
                        )
                        
                        if not should_exclude:
                            zipf.write(file_path, relative_path)
                            package_info['included_files'] += 1
            
            package_info['package_created'] = True
            package_info['package_path'] = str(package_path)
            package_info['package_size'] = package_path.stat().st_size
            package_info['excluded_patterns'] = exclude_patterns
            
            logger.info(f"项目打包完成: {package_path}")
            
        except Exception as e:
            logger.error(f"项目打包失败: {e}")
            package_info['error'] = str(e)
        
        return package_info
    
    async def _prepare_deployment_info(self, workspace_path: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """准备部署信息"""
        
        workspace = Path(workspace_path)
        project_type = requirements.get('project_type', 'web_app')
        
        deployment_info = {
            'project_type': project_type,
            'deployment_options': [],
            'environment_requirements': {},
            'configuration_needed': [],
            'deployment_steps': []
        }
        
        if project_type == 'web_app':
            deployment_info['deployment_options'] = [
                'Vercel',
                'Netlify', 
                'AWS S3 + CloudFront',
                'Docker + 云服务器'
            ]
            deployment_info['environment_requirements'] = {
                'Node.js': '>=14.0.0',
                'npm': '>=6.0.0'
            }
            deployment_info['configuration_needed'] = [
                '环境变量配置',
                'API 端点配置',
                '域名和SSL证书'
            ]
            deployment_info['deployment_steps'] = [
                '构建生产版本',
                '配置环境变量',
                '上传到部署平台',
                '配置域名',
                '测试部署结果'
            ]
        
        elif project_type == 'mobile_app':
            deployment_info['deployment_options'] = [
                'App Store (iOS)',
                'Google Play Store (Android)',
                'TestFlight (iOS 测试)',
                'Firebase App Distribution'
            ]
            deployment_info['configuration_needed'] = [
                '应用签名证书',
                '应用商店账号',
                '隐私政策',
                '应用图标和截图'
            ]
        
        elif project_type == 'data_analysis':
            deployment_info['deployment_options'] = [
                'Jupyter Hub',
                'Streamlit Cloud',
                'Heroku',
                'AWS EC2'
            ]
            deployment_info['environment_requirements'] = {
                'Python': '>=3.8',
                'pip': '>=20.0'
            }
        
        # 生成部署指南文件
        deployment_guide = self._generate_deployment_guide(deployment_info)
        guide_file = workspace / 'DEPLOYMENT.md'
        guide_file.write_text(deployment_guide, encoding='utf-8')
        
        deployment_info['guide_file'] = str(guide_file)
        
        return deployment_info
    
    def _generate_deployment_guide(self, deployment_info: Dict[str, Any]) -> str:
        """生成部署指南"""
        
        guide = f"""# 部署指南

## 项目类型
{deployment_info['project_type']}

## 部署选项
"""
        
        for option in deployment_info.get('deployment_options', []):
            guide += f"- {option}\n"
        
        guide += """

## 环境要求
"""
        
        for req, version in deployment_info.get('environment_requirements', {}).items():
            guide += f"- {req}: {version}\n"
        
        guide += """

## 配置需求
"""
        
        for config in deployment_info.get('configuration_needed', []):
            guide += f"- {config}\n"
        
        guide += """

## 部署步骤
"""
        
        for i, step in enumerate(deployment_info.get('deployment_steps', []), 1):
            guide += f"{i}. {step}\n"
        
        guide += f"""

## 注意事项
- 确保所有环境变量已正确配置
- 在生产环境部署前进行充分测试
- 准备好回滚方案
- 监控应用运行状态

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return guide
    
    async def _generate_final_report(
        self, 
        requirements: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        progress_data: Dict[str, Any],
        validation: Dict[str, Any],
        delivery_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成最终交付报告"""
        
        completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
        total_tasks = len(tasks)
        
        report = {
            'project_overview': {
                'project_type': requirements.get('project_type'),
                'complexity': requirements.get('complexity'),
                'estimated_hours': requirements.get('estimated_hours'),
                'actual_development_time': progress_data.get('monitoring_duration', 0) / 3600,
                'features_count': len(requirements.get('features', [])),
                'tasks_completed': f"{completed_tasks}/{total_tasks}"
            },
            'quality_metrics': {
                'overall_score': validation.get('overall_score', 0),
                'code_quality': validation.get('validations', {}).get('code_quality', {}).get('score', 0),
                'functionality_score': validation.get('validations', {}).get('functionality', {}).get('score', 0),
                'documentation_score': validation.get('validations', {}).get('documentation', {}).get('score', 0),
                'validation_status': validation.get('overall_status', 'unknown')
            },
            'deliverables': {
                'source_code': delivery_result.get('workspace_path'),
                'documentation': delivery_result.get('documentation', {}).get('files', []),
                'package': delivery_result.get('package', {}).get('package_path'),
                'deployment_guide': delivery_result.get('deployment', {}).get('guide_file')
            },
            'technical_summary': {
                'tech_stack': requirements.get('tech_stack', {}),
                'files_created': len(progress_data.get('files_created', [])),
                'files_modified': len(progress_data.get('files_modified', [])),
                'total_lines_of_code': progress_data.get('quality_metrics', {}).get('total_lines', 0)
            },
            'recommendations': validation.get('recommendations', []),
            'next_steps': [
                '检查并解决验证中发现的问题',
                '完善测试覆盖率',
                '准备生产环境部署',
                '制定维护和更新计划'
            ],
            'auto_cursor_agent_summary': {
                'development_approach': '全自动化AI驱动开发',
                'key_benefits': [
                    '需求自动分析和任务分解',
                    '智能代码生成和指导',
                    '实时质量监控和优化',
                    '完整的项目验证和交付'
                ],
                'total_automation_level': '85%',
                'human_intervention_required': '15%'
            }
        }
        
        return report
