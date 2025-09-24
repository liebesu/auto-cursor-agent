#!/usr/bin/env python3
"""
Auto Cursor Agent - 自动化Cursor交互开发代理

主要功能：
- 理解用户的模糊需求
- 自动与Cursor进行交互
- 实现全自动化的软件开发流程
"""

import asyncio
import sys
import argparse
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.need_analyzer import NeedAnalyzer
from core.task_orchestrator import TaskOrchestrator
from core.cursor_interface import CursorInterface
from core.progress_monitor import ProgressMonitor
from core.auto_optimizer import AutoOptimizer
from core.delivery_manager import DeliveryManager
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logger


class AutoCursorAgent:
    """Auto Cursor Agent 主类"""
    
    def __init__(self, config_path: str = None):
        """初始化代理"""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 设置日志
        setup_logger(self.config.get('logging', {}))
        
        # 初始化核心组件
        self.need_analyzer = NeedAnalyzer(self.config)
        self.task_orchestrator = TaskOrchestrator(self.config)
        self.cursor_interface = CursorInterface(self.config)
        self.progress_monitor = ProgressMonitor(self.config)
        self.auto_optimizer = AutoOptimizer(self.config)
        self.delivery_manager = DeliveryManager(self.config)
        
        logger.info("Auto Cursor Agent 已初始化")
    
    async def process_requirement(self, requirement: str, workspace_path: str = None):
        """处理用户需求"""
        try:
            logger.info(f"开始处理需求: {requirement}")
            
            # 1. 分析需求
            logger.info("第一阶段: 需求分析")
            analyzed_requirement = await self.need_analyzer.analyze(requirement)
            
            # 2. 分解任务
            logger.info("第二阶段: 任务分解")
            tasks = await self.task_orchestrator.decompose_tasks(analyzed_requirement)
            
            # 3. 启动监控
            logger.info("第三阶段: 启动进度监控")
            if workspace_path:
                self.progress_monitor.start_monitoring(workspace_path)
            
            # 4. 执行开发任务
            logger.info("第四阶段: 开始自动化开发")
            results = await self.execute_development(tasks, workspace_path, analyzed_requirement)
            
            # 5. 优化和质量保证
            logger.info("第五阶段: 质量优化和验证")
            optimization_result = await self.optimize_and_validate(tasks, workspace_path, analyzed_requirement)
            
            # 6. 项目交付
            logger.info("第六阶段: 准备项目交付")
            delivery_result = await self.prepare_delivery(tasks, workspace_path, analyzed_requirement, results)
            
            # 7. 生成最终报告
            logger.info("第七阶段: 生成完整报告")
            report = await self.generate_completion_report(results, optimization_result, delivery_result)
            
            logger.success("需求处理完成!")
            return report
            
        except Exception as e:
            logger.error(f"处理需求时发生错误: {e}")
            raise
    
    async def execute_development(self, tasks: list, workspace_path: str, analyzed_requirement: Dict[str, Any]):
        """执行开发任务"""
        results = []
        
        # 启动监控
        self.progress_monitor.start_monitoring(workspace_path)
        
        # 启动持续优化（后台任务）
        optimization_task = asyncio.create_task(
            self.auto_optimizer.continuous_optimization(tasks, self.progress_monitor)
        )
        
        try:
            for task in tasks:
                logger.info(f"执行任务: {task.get('name', 'Unknown')}")
                
                try:
                    # 与Cursor交互执行任务
                    result = await self.cursor_interface.execute_task(task, workspace_path)
                    results.append(result)
                    
                    # 更新任务状态
                    self.task_orchestrator.update_task_status(tasks, task['id'], 'completed')
                    
                    # 检查进度
                    progress = self.progress_monitor.get_progress()
                    logger.info(f"当前进度: {progress.get('completion_rate', 0):.1%}")
                    
                    # 周期性优化检查
                    if len(results) % 3 == 0:  # 每3个任务检查一次
                        progress_data = self.progress_monitor.get_detailed_report()
                        optimization = await self.auto_optimizer.optimize_development_process(
                            tasks, progress_data['progress_data']
                        )
                        
                        if optimization.get('adjustments'):
                            logger.info("应用开发策略调整")
                            tasks = optimization.get('optimized_tasks', tasks)
                    
                except Exception as e:
                    logger.error(f"执行任务 {task.get('name')} 时出错: {e}")
                    results.append({"error": str(e), "task": task})
                    self.task_orchestrator.update_task_status(tasks, task['id'], 'failed')
            
        finally:
            # 停止监控和优化
            self.progress_monitor.stop_monitoring()
            optimization_task.cancel()
            try:
                await optimization_task
            except asyncio.CancelledError:
                pass
        
        return results
    
    async def optimize_and_validate(self, tasks: list, workspace_path: str, analyzed_requirement: Dict[str, Any]):
        """优化和验证项目"""
        logger.info("开始项目优化和验证")
        
        # 获取最终进度数据
        progress_data = self.progress_monitor.get_detailed_report()
        
        # 执行最终优化
        optimization_result = await self.auto_optimizer.optimize_development_process(
            tasks, progress_data['progress_data']
        )
        
        logger.success("项目优化完成")
        return optimization_result
    
    async def prepare_delivery(
        self, 
        tasks: list, 
        workspace_path: str, 
        analyzed_requirement: Dict[str, Any], 
        development_results: list
    ):
        """准备项目交付"""
        logger.info("开始准备项目交付")
        
        # 获取进度数据
        progress_data = self.progress_monitor.get_detailed_report()
        
        # 执行交付准备
        delivery_result = await self.delivery_manager.prepare_delivery(
            workspace_path, 
            analyzed_requirement, 
            tasks, 
            progress_data['progress_data']
        )
        
        logger.success(f"项目交付准备完成，状态: {delivery_result.get('status')}")
        return delivery_result
    
    async def generate_completion_report(
        self, 
        development_results: list, 
        optimization_result: dict, 
        delivery_result: dict
    ) -> dict:
        """生成完整的完成报告"""
        
        # 统计开发结果
        successful_tasks = len([r for r in development_results if "error" not in r])
        failed_tasks = len([r for r in development_results if "error" in r])
        
        # 获取优化报告
        optimization_report = self.auto_optimizer.get_optimization_report()
        
        # 生成综合报告
        report = {
            "overall_status": "completed",
            "timestamp": time.time(),
            "development": {
                "total_tasks": len(development_results),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": successful_tasks / len(development_results) if development_results else 0,
                "results": development_results
            },
            "optimization": {
                "optimizations_performed": optimization_report.get('total_optimizations', 0),
                "optimization_effectiveness": optimization_report.get('effectiveness', 0),
                "final_quality_score": optimization_result.get('assessment', {}).get('overall_score', 0)
            },
            "delivery": {
                "status": delivery_result.get('status'),
                "validation_score": delivery_result.get('validation', {}).get('overall_score', 0),
                "deliverables": delivery_result.get('final_report', {}).get('deliverables', {}),
                "package_created": delivery_result.get('package', {}).get('package_created', False)
            },
            "summary": {
                "project_ready": delivery_result.get('status') in ['ready_for_delivery', 'ready_with_warnings'],
                "quality_score": delivery_result.get('validation', {}).get('overall_score', 0),
                "automation_level": "95%",
                "manual_review_required": delivery_result.get('status') == 'ready_with_warnings'
            },
            "auto_cursor_agent": {
                "version": "1.0.0",
                "approach": "Full AI-Driven Development",
                "key_achievements": [
                    "自动需求分析和技术方案设计",
                    "智能任务分解和依赖管理",
                    "自动化Cursor交互和代码指导",
                    "实时质量监控和策略调整",
                    "完整的项目验证和交付准备"
                ]
            }
        }
        
        return report


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Auto Cursor Agent - 自动化开发代理")
    parser.add_argument("--requirement", "-r", required=True, help="开发需求描述")
    parser.add_argument("--workspace", "-w", help="工作空间路径")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--debug", "-d", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 创建代理实例
    agent = AutoCursorAgent(args.config)
    
    try:
        # 处理需求
        report = await agent.process_requirement(
            requirement=args.requirement,
            workspace_path=args.workspace
        )
        
        logger.success("开发完成!")
        logger.info(f"完成报告: {report}")
        
    except KeyboardInterrupt:
        logger.warning("用户中断了程序")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())
