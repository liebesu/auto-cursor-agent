"""
进度监控器模块

负责实时监控文件变化、代码质量、测试结果
"""

import asyncio
import time
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from loguru import logger

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class FileMonitorHandler(FileSystemEventHandler):
    """文件监控处理器"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        super().__init__()
    
    def on_modified(self, event):
        if not event.is_directory:
            self.monitor._on_file_changed('modified', event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self.monitor._on_file_changed('created', event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.monitor._on_file_changed('deleted', event.src_path)


class CodeQualityAnalyzer:
    """代码质量分析器"""
    
    def __init__(self):
        self.quality_metrics = {
            'complexity': 0,
            'maintainability': 0,
            'readability': 0,
            'test_coverage': 0,
            'documentation': 0
        }
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """分析Python文件质量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 计算复杂度
            complexity = self._calculate_complexity(tree)
            
            # 检查文档字符串
            documentation = self._check_documentation(tree)
            
            # 检查代码风格
            style_score = self._check_code_style(content)
            
            return {
                'complexity': min(complexity / 10, 1.0),  # 标准化到0-1
                'documentation': documentation,
                'style_score': style_score,
                'lines_of_code': len(content.split('\n')),
                'functions_count': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                'classes_count': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            }
            
        except Exception as e:
            logger.warning(f"分析Python文件失败 {file_path}: {e}")
            return {'error': str(e)}
    
    def analyze_javascript_file(self, file_path: Path) -> Dict[str, Any]:
        """分析JavaScript文件质量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的JavaScript质量检查
            lines = content.split('\n')
            
            # 检查基本结构
            has_functions = 'function' in content or '=>' in content
            has_comments = any(line.strip().startswith('//') or '/*' in line for line in lines)
            has_error_handling = 'try' in content and 'catch' in content
            
            # 计算分数
            quality_score = 0
            if has_functions:
                quality_score += 0.3
            if has_comments:
                quality_score += 0.3
            if has_error_handling:
                quality_score += 0.2
            if len(lines) < 200:  # 文件不太长
                quality_score += 0.2
            
            return {
                'quality_score': quality_score,
                'lines_of_code': len(lines),
                'has_functions': has_functions,
                'has_comments': has_comments,
                'has_error_handling': has_error_handling
            }
            
        except Exception as e:
            logger.warning(f"分析JavaScript文件失败 {file_path}: {e}")
            return {'error': str(e)}
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """计算代码复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 1
        
        return complexity
    
    def _check_documentation(self, tree: ast.AST) -> float:
        """检查文档覆盖率"""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        total_items = len(functions) + len(classes)
        if total_items == 0:
            return 1.0
        
        documented_items = 0
        
        for func in functions:
            if ast.get_docstring(func):
                documented_items += 1
        
        for cls in classes:
            if ast.get_docstring(cls):
                documented_items += 1
        
        return documented_items / total_items
    
    def _check_code_style(self, content: str) -> float:
        """检查代码风格"""
        lines = content.split('\n')
        
        style_score = 1.0
        
        # 检查长行
        long_lines = sum(1 for line in lines if len(line) > 120)
        if long_lines > len(lines) * 0.1:  # 超过10%的行太长
            style_score -= 0.2
        
        # 检查空行使用
        empty_lines = sum(1 for line in lines if not line.strip())
        if empty_lines < len(lines) * 0.05:  # 空行太少
            style_score -= 0.1
        
        # 检查注释
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if comment_lines < len(lines) * 0.1:  # 注释太少
            style_score -= 0.2
        
        return max(style_score, 0.0)


class ProgressMonitor:
    """进度监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化进度监控器"""
        self.config = config
        self.monitoring_config = config.get('monitoring', {})
        self.is_monitoring = False
        self.workspace_path = None
        
        # 监控数据
        self.file_changes = []
        self.quality_history = []
        self.progress_data = {
            'start_time': None,
            'files_created': [],
            'files_modified': [],
            'files_deleted': [],
            'quality_metrics': {},
            'test_results': {},
            'completion_estimates': []
        }
        
        # 文件监控
        self.observer = None
        self.file_handler = None
        
        # 代码质量分析器
        self.quality_analyzer = CodeQualityAnalyzer()
        
        # 监控配置
        self.check_interval = self.monitoring_config.get('check_interval', 30)
        self.file_patterns = self.monitoring_config.get('file_patterns', ['*.py', '*.js', '*.ts', '*.tsx'])
        self.ignore_patterns = self.monitoring_config.get('ignore_patterns', ['.git', 'node_modules', '__pycache__'])
        
        logger.info("进度监控器已初始化")
    
    def start_monitoring(self, workspace_path: str):
        """开始监控"""
        logger.info(f"开始监控工作空间: {workspace_path}")
        
        self.workspace_path = Path(workspace_path)
        self.is_monitoring = True
        self.progress_data['start_time'] = time.time()
        
        # 启动文件监控
        if WATCHDOG_AVAILABLE:
            self._start_file_monitoring()
        else:
            logger.warning("Watchdog不可用，使用轮询监控")
        
        # 启动后台监控任务
        asyncio.create_task(self._monitoring_loop())
        
        logger.success("监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        logger.info("停止监控")
        self.is_monitoring = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def _start_file_monitoring(self):
        """启动文件监控"""
        if not self.workspace_path.exists():
            return
        
        self.file_handler = FileMonitorHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.file_handler, str(self.workspace_path), recursive=True)
        self.observer.start()
        
        logger.info("文件监控已启动")
    
    def _on_file_changed(self, change_type: str, file_path: str):
        """文件变化回调"""
        file_path = Path(file_path)
        
        # 检查是否应该忽略
        if self._should_ignore_file(file_path):
            return
        
        relative_path = str(file_path.relative_to(self.workspace_path))
        
        change_info = {
            'type': change_type,
            'path': relative_path,
            'timestamp': time.time(),
            'size': file_path.stat().st_size if file_path.exists() else 0
        }
        
        self.file_changes.append(change_info)
        
        # 更新进度数据
        if change_type == 'created':
            if relative_path not in self.progress_data['files_created']:
                self.progress_data['files_created'].append(relative_path)
        elif change_type == 'modified':
            if relative_path not in self.progress_data['files_modified']:
                self.progress_data['files_modified'].append(relative_path)
        elif change_type == 'deleted':
            if relative_path not in self.progress_data['files_deleted']:
                self.progress_data['files_deleted'].append(relative_path)
        
        logger.debug(f"文件变化: {change_type} - {relative_path}")
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """检查是否应该忽略文件"""
        file_str = str(file_path)
        
        # 检查忽略模式
        for pattern in self.ignore_patterns:
            if pattern in file_str:
                return True
        
        # 检查文件扩展名
        if self.file_patterns:
            file_extension = file_path.suffix
            matched = False
            for pattern in self.file_patterns:
                if pattern.replace('*', '') == file_extension:
                    matched = True
                    break
            if not matched:
                return True
        
        return False
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 更新质量指标
                await self._update_quality_metrics()
                
                # 检测测试结果
                await self._check_test_results()
                
                # 估算完成度
                await self._estimate_completion()
                
                # 清理旧数据
                self._cleanup_old_data()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _update_quality_metrics(self):
        """更新代码质量指标"""
        if not self.workspace_path or not self.workspace_path.exists():
            return
        
        quality_metrics = {
            'timestamp': time.time(),
            'files_analyzed': 0,
            'average_quality': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'issues_found': []
        }
        
        total_quality = 0
        files_analyzed = 0
        
        # 分析工作空间中的文件
        for file_path in self.workspace_path.rglob("*"):
            if not file_path.is_file() or self._should_ignore_file(file_path):
                continue
            
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.py':
                analysis = self.quality_analyzer.analyze_python_file(file_path)
                if 'error' not in analysis:
                    files_analyzed += 1
                    file_quality = (
                        analysis.get('style_score', 0) * 0.4 +
                        analysis.get('documentation', 0) * 0.3 +
                        (1 - analysis.get('complexity', 0)) * 0.3
                    )
                    total_quality += file_quality
                    quality_metrics['total_lines'] += analysis.get('lines_of_code', 0)
                    quality_metrics['total_functions'] += analysis.get('functions_count', 0)
                    quality_metrics['total_classes'] += analysis.get('classes_count', 0)
            
            elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                analysis = self.quality_analyzer.analyze_javascript_file(file_path)
                if 'error' not in analysis:
                    files_analyzed += 1
                    file_quality = analysis.get('quality_score', 0)
                    total_quality += file_quality
                    quality_metrics['total_lines'] += analysis.get('lines_of_code', 0)
        
        # 计算平均质量
        if files_analyzed > 0:
            quality_metrics['files_analyzed'] = files_analyzed
            quality_metrics['average_quality'] = total_quality / files_analyzed
        
        # 保存质量数据
        self.progress_data['quality_metrics'] = quality_metrics
        self.quality_history.append(quality_metrics)
        
        # 限制历史记录数量
        if len(self.quality_history) > 100:
            self.quality_history = self.quality_history[-50:]
    
    async def _check_test_results(self):
        """检查测试结果"""
        test_results = {
            'timestamp': time.time(),
            'tests_found': False,
            'tests_passed': 0,
            'tests_failed': 0,
            'coverage': 0
        }
        
        # 检查常见的测试文件
        test_files = []
        if self.workspace_path:
            test_patterns = ['test_*.py', '*_test.py', '*.test.js', '*.spec.js']
            for pattern in test_patterns:
                test_files.extend(self.workspace_path.rglob(pattern))
        
        if test_files:
            test_results['tests_found'] = True
            test_results['test_files_count'] = len(test_files)
            
            # 简单的测试分析（在实际项目中可以运行测试获取真实结果）
            test_results['estimated_coverage'] = min(len(test_files) * 0.1, 0.8)
        
        self.progress_data['test_results'] = test_results
    
    async def _estimate_completion(self):
        """估算完成度"""
        if not self.progress_data['start_time']:
            return
        
        # 基于文件变化估算进度
        total_files_changed = (
            len(self.progress_data['files_created']) +
            len(self.progress_data['files_modified'])
        )
        
        # 基于时间估算
        elapsed_time = time.time() - self.progress_data['start_time']
        
        # 基于代码质量估算
        quality_score = self.progress_data.get('quality_metrics', {}).get('average_quality', 0)
        
        # 综合估算
        file_progress = min(total_files_changed * 0.1, 0.7)  # 文件变化权重
        time_progress = min(elapsed_time / 3600, 0.3)  # 时间权重（假设1小时完成30%）
        quality_progress = quality_score * 0.2  # 质量权重
        
        completion_estimate = file_progress + time_progress + quality_progress
        completion_estimate = min(completion_estimate, 1.0)
        
        estimation = {
            'timestamp': time.time(),
            'completion_rate': completion_estimate,
            'file_progress': file_progress,
            'time_progress': time_progress,
            'quality_progress': quality_progress,
            'total_files_changed': total_files_changed,
            'elapsed_hours': elapsed_time / 3600
        }
        
        self.progress_data['completion_estimates'].append(estimation)
        
        # 限制历史记录
        if len(self.progress_data['completion_estimates']) > 50:
            self.progress_data['completion_estimates'] = self.progress_data['completion_estimates'][-25:]
    
    def _cleanup_old_data(self):
        """清理旧数据"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 保留1小时内的数据
        
        # 清理文件变化记录
        self.file_changes = [
            change for change in self.file_changes
            if change.get('timestamp', 0) > cutoff_time
        ]
    
    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        if not self.is_monitoring:
            return {"status": "not_monitoring"}
        
        # 获取最新的完成度估算
        latest_estimate = {}
        if self.progress_data['completion_estimates']:
            latest_estimate = self.progress_data['completion_estimates'][-1]
        
        # 获取最新的质量指标
        quality_metrics = self.progress_data.get('quality_metrics', {})
        
        # 计算最近的活动
        recent_changes = [
            change for change in self.file_changes
            if change.get('timestamp', 0) > time.time() - 300  # 最近5分钟
        ]
        
        progress = {
            "status": "monitoring",
            "completion_rate": latest_estimate.get('completion_rate', 0),
            "quality_score": quality_metrics.get('average_quality', 0),
            "files_created": len(self.progress_data['files_created']),
            "files_modified": len(self.progress_data['files_modified']),
            "files_deleted": len(self.progress_data['files_deleted']),
            "total_lines": quality_metrics.get('total_lines', 0),
            "recent_activity": len(recent_changes),
            "monitoring_duration": time.time() - self.progress_data.get('start_time', time.time()),
            "last_update": datetime.now().isoformat(),
            "test_coverage": self.progress_data.get('test_results', {}).get('estimated_coverage', 0),
            "quality_trend": self._calculate_quality_trend()
        }
        
        return progress
    
    def _calculate_quality_trend(self) -> str:
        """计算质量趋势"""
        if len(self.quality_history) < 2:
            return "stable"
        
        recent_quality = self.quality_history[-1].get('average_quality', 0)
        previous_quality = self.quality_history[-2].get('average_quality', 0)
        
        if recent_quality > previous_quality + 0.1:
            return "improving"
        elif recent_quality < previous_quality - 0.1:
            return "declining"
        else:
            return "stable"
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """获取详细的监控报告"""
        return {
            "monitoring_status": "active" if self.is_monitoring else "inactive",
            "workspace_path": str(self.workspace_path) if self.workspace_path else None,
            "progress_data": self.progress_data,
            "recent_file_changes": self.file_changes[-20:],  # 最近20个变化
            "quality_history": self.quality_history[-10:],   # 最近10个质量记录
            "summary": self.get_progress()
        }
    
    def export_report(self, output_path: str):
        """导出监控报告"""
        report = self.get_detailed_report()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"监控报告已导出: {output_path}")
