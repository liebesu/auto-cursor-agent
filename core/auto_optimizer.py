"""
自动优化器模块

负责根据监控结果自动调整开发策略和流程
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from loguru import logger
from .ai_models import AIModelManager


class QualityAssessment:
    """质量评估器"""
    
    def __init__(self):
        self.quality_thresholds = {
            'code_quality': 0.7,
            'test_coverage': 0.6,
            'documentation': 0.5,
            'complexity': 0.8,
            'maintainability': 0.7
        }
    
    def assess_project_quality(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估项目整体质量"""
        
        quality_metrics = progress_data.get('quality_metrics', {})
        test_results = progress_data.get('test_results', {})
        
        assessment = {
            'overall_score': 0,
            'code_quality': quality_metrics.get('average_quality', 0),
            'test_coverage': test_results.get('estimated_coverage', 0),
            'file_count': len(progress_data.get('files_created', [])) + len(progress_data.get('files_modified', [])),
            'complexity_score': 1 - quality_metrics.get('complexity', 0),
            'documentation_score': quality_metrics.get('documentation', 0),
            'issues': [],
            'recommendations': []
        }
        
        # 计算综合评分
        weights = {
            'code_quality': 0.3,
            'test_coverage': 0.2,
            'complexity_score': 0.2,
            'documentation_score': 0.3
        }
        
        total_score = 0
        for metric, weight in weights.items():
            total_score += assessment[metric] * weight
        
        assessment['overall_score'] = total_score
        
        # 识别问题
        issues = []
        recommendations = []
        
        if assessment['code_quality'] < self.quality_thresholds['code_quality']:
            issues.append(f"代码质量偏低 ({assessment['code_quality']:.2f} < {self.quality_thresholds['code_quality']})")
            recommendations.append("建议重构代码，改善代码结构和可读性")
        
        if assessment['test_coverage'] < self.quality_thresholds['test_coverage']:
            issues.append(f"测试覆盖率不足 ({assessment['test_coverage']:.2f} < {self.quality_thresholds['test_coverage']})")
            recommendations.append("需要增加单元测试和集成测试")
        
        if assessment['documentation_score'] < self.quality_thresholds['documentation']:
            issues.append(f"文档覆盖率不足 ({assessment['documentation_score']:.2f} < {self.quality_thresholds['documentation']})")
            recommendations.append("需要完善函数和类的文档字符串")
        
        if assessment['complexity_score'] < self.quality_thresholds['complexity']:
            issues.append(f"代码复杂度过高 ({assessment['complexity_score']:.2f} < {self.quality_thresholds['complexity']})")
            recommendations.append("建议简化复杂函数，拆分为更小的函数")
        
        assessment['issues'] = issues
        assessment['recommendations'] = recommendations
        
        return assessment
    
    def assess_task_progress(self, task: Dict[str, Any], progress_info: Dict[str, Any]) -> Dict[str, Any]:
        """评估单个任务的进展情况"""
        
        task_assessment = {
            'task_id': task.get('id'),
            'task_name': task.get('name'),
            'status': task.get('status', 'unknown'),
            'progress_score': progress_info.get('completion_rate', 0),
            'time_efficiency': 1.0,
            'quality_issues': [],
            'blocking_factors': [],
            'next_actions': []
        }
        
        # 计算时间效率
        estimated_hours = task.get('estimated_hours', 4)
        if 'started_at' in task:
            elapsed_time = time.time() - task['started_at']
            elapsed_hours = elapsed_time / 3600
            
            if elapsed_hours > 0:
                task_assessment['time_efficiency'] = min(estimated_hours / elapsed_hours, 2.0)
        
        # 分析进展情况
        if task_assessment['progress_score'] < 0.3 and task_assessment['time_efficiency'] < 0.5:
            task_assessment['blocking_factors'].append("进展缓慢，可能遇到技术难题")
            task_assessment['next_actions'].append("需要重新评估任务复杂度或寻求技术支持")
        
        if task_assessment['progress_score'] > 0.8:
            task_assessment['next_actions'].append("准备进入测试和验证阶段")
        
        return task_assessment
    
    def generate_improvement_plan(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """生成改进计划"""
        
        plan = {
            'priority_actions': [],
            'short_term_goals': [],
            'long_term_goals': [],
            'resource_needs': [],
            'timeline': {}
        }
        
        # 根据评估结果生成改进计划
        if assessment['overall_score'] < 0.6:
            plan['priority_actions'].append("立即进行代码质量改进")
            plan['short_term_goals'].append("将整体质量分数提升到0.7以上")
        
        if assessment['test_coverage'] < 0.5:
            plan['priority_actions'].append("增加测试覆盖率")
            plan['resource_needs'].append("分配时间编写测试用例")
        
        if assessment['documentation_score'] < 0.4:
            plan['short_term_goals'].append("完善关键模块的文档")
            plan['timeline']['documentation'] = "1-2天内完成"
        
        return plan


class StrategyAdjuster:
    """策略调整器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # 检查是否启用测试模式
        test_mode = config.get('ai_models', {}).get('test_mode', {}).get('enabled', False)
        if test_mode:
            from core.test_ai_model import TestAIModelManager
            self.ai_manager = TestAIModelManager(config)
        else:
            self.ai_manager = AIModelManager(config)
        self.adjustment_history = []
    
    async def adjust_development_strategy(
        self, 
        tasks: List[Dict[str, Any]], 
        assessment: Dict[str, Any],
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调整开发策略"""
        
        logger.info("正在分析并调整开发策略")
        
        adjustment = {
            'timestamp': time.time(),
            'trigger': assessment.get('issues', []),
            'adjustments': [],
            'new_priorities': [],
            'resource_reallocation': {},
            'timeline_changes': {}
        }
        
        # 基于质量评估调整策略
        if assessment['overall_score'] < 0.6:
            adjustment['adjustments'].append({
                'type': 'quality_focus',
                'description': '将重点转向质量改进',
                'actions': [
                    '暂停新功能开发',
                    '优先修复质量问题',
                    '增加代码审查频率'
                ]
            })
        
        # 基于进度调整优先级
        if assessment.get('progress_score', 0) < 0.5:
            adjustment['adjustments'].append({
                'type': 'priority_adjustment',
                'description': '重新调整任务优先级',
                'actions': [
                    '识别关键路径任务',
                    '暂停低优先级任务',
                    '集中资源完成核心功能'
                ]
            })
        
        # 使用AI生成具体的调整建议
        ai_suggestions = await self._generate_ai_suggestions(tasks, assessment, progress_data)
        if ai_suggestions:
            adjustment['ai_suggestions'] = ai_suggestions
        
        # 记录调整历史
        self.adjustment_history.append(adjustment)
        
        logger.info(f"策略调整完成，生成 {len(adjustment['adjustments'])} 项调整建议")
        return adjustment
    
    async def _generate_ai_suggestions(
        self, 
        tasks: List[Dict[str, Any]], 
        assessment: Dict[str, Any],
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用AI生成调整建议"""
        
        try:
            # 构建分析提示
            prompt = f"""
作为一个经验丰富的项目管理专家和技术架构师，请分析当前项目状况并提供调整建议：

项目质量评估：
- 整体评分：{assessment.get('overall_score', 0):.2f}
- 代码质量：{assessment.get('code_quality', 0):.2f}
- 测试覆盖率：{assessment.get('test_coverage', 0):.2f}
- 文档完整度：{assessment.get('documentation_score', 0):.2f}

发现的问题：
{chr(10).join(f"- {issue}" for issue in assessment.get('issues', []))}

当前任务状态：
- 总任务数：{len(tasks)}
- 已完成：{len([t for t in tasks if t.get('status') == 'completed'])}
- 进行中：{len([t for t in tasks if t.get('status') == 'in_progress'])}

请提供：
1. 最重要的3个调整建议
2. 具体的执行步骤
3. 预期的改进效果
4. 风险评估

返回JSON格式：
{{
  "priority_adjustments": [
    {{
      "title": "调整建议标题",
      "description": "详细描述",
      "steps": ["步骤1", "步骤2"],
      "expected_impact": "预期效果",
      "risk_level": "low/medium/high"
    }}
  ],
  "timeline_recommendation": "建议的时间安排",
  "success_metrics": ["成功指标1", "成功指标2"]
}}
"""
            
            response = await self.ai_manager.generate_response(prompt)
            
            # 解析AI响应
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group(0))
                return suggestions
            
        except Exception as e:
            logger.warning(f"AI建议生成失败: {e}")
        
        return {}
    
    def apply_adjustments(
        self, 
        tasks: List[Dict[str, Any]], 
        adjustment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """应用策略调整"""
        
        adjusted_tasks = tasks.copy()
        
        for adj in adjustment.get('adjustments', []):
            if adj['type'] == 'priority_adjustment':
                # 重新调整任务优先级
                adjusted_tasks = self._adjust_task_priorities(adjusted_tasks)
            elif adj['type'] == 'quality_focus':
                # 添加质量改进任务
                adjusted_tasks = self._add_quality_tasks(adjusted_tasks)
        
        logger.info(f"应用了 {len(adjustment.get('adjustments', []))} 项策略调整")
        return adjusted_tasks
    
    def _adjust_task_priorities(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """调整任务优先级"""
        
        # 提升核心任务的优先级
        core_task_types = ['setup', 'database', 'core_features']
        
        for task in tasks:
            if task.get('type') in core_task_types and task.get('status') != 'completed':
                task['priority'] = max(task.get('priority', 3) + 1, 5)
                task['adjusted'] = True
        
        # 重新排序
        tasks.sort(key=lambda x: (-x.get('priority', 3), x.get('execution_order', 0)))
        
        return tasks
    
    def _add_quality_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """添加质量改进任务"""
        
        quality_tasks = [
            {
                'id': 'quality_review',
                'name': '代码质量审查',
                'description': '对现有代码进行质量审查和改进',
                'type': 'quality',
                'priority': 5,
                'estimated_hours': 2,
                'status': 'pending',
                'subtasks': [
                    '检查代码风格一致性',
                    '优化函数复杂度',
                    '添加必要注释',
                    '重构重复代码'
                ]
            },
            {
                'id': 'test_enhancement',
                'name': '测试覆盖率提升',
                'description': '增加单元测试和集成测试',
                'type': 'testing',
                'priority': 4,
                'estimated_hours': 3,
                'status': 'pending',
                'subtasks': [
                    '编写核心功能单元测试',
                    '添加边界条件测试',
                    '实现集成测试',
                    '验证测试覆盖率'
                ]
            }
        ]
        
        # 在适当位置插入质量任务
        insertion_point = len([t for t in tasks if t.get('status') == 'completed'])
        
        for i, quality_task in enumerate(quality_tasks):
            tasks.insert(insertion_point + i, quality_task)
        
        return tasks


class AutoOptimizer:
    """自动优化器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化自动优化器"""
        self.config = config
        self.quality_assessor = QualityAssessment()
        self.strategy_adjuster = StrategyAdjuster(config)
        self.optimization_history = []
        
        # 优化配置
        self.optimization_config = config.get('optimization', {})
        self.auto_adjust_enabled = self.optimization_config.get('auto_adjust', True)
        self.quality_threshold = self.optimization_config.get('quality_threshold', 0.7)
        self.check_interval = self.optimization_config.get('check_interval', 300)  # 5分钟
        
        logger.info("自动优化器已初始化")
    
    async def optimize_development_process(
        self, 
        tasks: List[Dict[str, Any]], 
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """优化开发流程"""
        
        logger.info("开始自动优化开发流程")
        
        optimization_result = {
            'timestamp': time.time(),
            'triggered_by': 'automatic_check',
            'assessment': {},
            'adjustments': {},
            'optimized_tasks': [],
            'recommendations': []
        }
        
        try:
            # 1. 质量评估
            assessment = self.quality_assessor.assess_project_quality(progress_data)
            optimization_result['assessment'] = assessment
            
            logger.info(f"质量评估完成，整体评分: {assessment['overall_score']:.2f}")
            
            # 2. 策略调整
            if assessment['overall_score'] < self.quality_threshold or assessment['issues']:
                adjustments = await self.strategy_adjuster.adjust_development_strategy(
                    tasks, assessment, progress_data
                )
                optimization_result['adjustments'] = adjustments
                
                # 3. 应用调整
                if self.auto_adjust_enabled:
                    optimized_tasks = self.strategy_adjuster.apply_adjustments(tasks, adjustments)
                    optimization_result['optimized_tasks'] = optimized_tasks
                    logger.info("自动策略调整已应用")
                else:
                    optimization_result['optimized_tasks'] = tasks
                    logger.info("策略调整建议已生成，等待手动确认")
            else:
                optimization_result['optimized_tasks'] = tasks
                logger.info("当前开发流程良好，无需调整")
            
            # 4. 生成改进计划
            improvement_plan = self.quality_assessor.generate_improvement_plan(assessment)
            optimization_result['improvement_plan'] = improvement_plan
            
            # 5. 记录优化历史
            self.optimization_history.append(optimization_result)
            
            logger.success("开发流程优化完成")
            
        except Exception as e:
            logger.error(f"自动优化过程出错: {e}")
            optimization_result['error'] = str(e)
            optimization_result['optimized_tasks'] = tasks
        
        return optimization_result
    
    async def continuous_optimization(
        self, 
        tasks: List[Dict[str, Any]], 
        progress_monitor
    ):
        """持续优化监控"""
        
        logger.info("启动持续优化监控")
        
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                
                # 获取最新进度数据
                progress_data = progress_monitor.get_detailed_report()
                
                # 执行优化
                optimization_result = await self.optimize_development_process(
                    tasks, progress_data['progress_data']
                )
                
                # 如果有重要调整，记录日志
                if optimization_result.get('adjustments'):
                    logger.warning(f"检测到 {len(optimization_result['adjustments'].get('adjustments', []))} 项需要调整的问题")
                
            except Exception as e:
                logger.error(f"持续优化监控出错: {e}")
                await asyncio.sleep(self.check_interval)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        
        if not self.optimization_history:
            return {"status": "no_optimizations_performed"}
        
        latest_optimization = self.optimization_history[-1]
        
        return {
            "total_optimizations": len(self.optimization_history),
            "latest_optimization": latest_optimization,
            "optimization_trend": self._calculate_optimization_trend(),
            "effectiveness": self._calculate_optimization_effectiveness(),
            "summary": {
                "auto_adjust_enabled": self.auto_adjust_enabled,
                "quality_threshold": self.quality_threshold,
                "check_interval": self.check_interval,
                "last_optimization": latest_optimization.get('timestamp', 0)
            }
        }
    
    def _calculate_optimization_trend(self) -> str:
        """计算优化趋势"""
        if len(self.optimization_history) < 2:
            return "insufficient_data"
        
        recent_scores = [
            opt['assessment'].get('overall_score', 0) 
            for opt in self.optimization_history[-3:]
            if 'assessment' in opt
        ]
        
        if len(recent_scores) < 2:
            return "insufficient_data"
        
        if recent_scores[-1] > recent_scores[-2]:
            return "improving"
        elif recent_scores[-1] < recent_scores[-2]:
            return "declining"
        else:
            return "stable"
    
    def _calculate_optimization_effectiveness(self) -> float:
        """计算优化效果"""
        if len(self.optimization_history) < 2:
            return 0.5
        
        improvements = 0
        total_optimizations = 0
        
        for i in range(1, len(self.optimization_history)):
            prev_score = self.optimization_history[i-1].get('assessment', {}).get('overall_score', 0)
            curr_score = self.optimization_history[i].get('assessment', {}).get('overall_score', 0)
            
            if curr_score > prev_score:
                improvements += 1
            total_optimizations += 1
        
        return improvements / total_optimizations if total_optimizations > 0 else 0.5

