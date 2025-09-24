#!/usr/bin/env python3
"""
Auto Cursor Agent 使用示例

演示完整的工作流程：从用户需求到项目完成
"""

import asyncio
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.need_analyzer import NeedAnalyzer
from core.task_orchestrator import TaskOrchestrator
from core.cursor_interface import CursorInterface
from core.progress_monitor import ProgressMonitor
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logger


async def demo_weather_app():
    """演示：创建天气预报应用"""
    
    print("🌤️ === Auto Cursor Agent 演示：天气预报应用 ===")
    print()
    
    # 1. 初始化系统
    print("📋 第一步：系统初始化")
    config_manager = ConfigManager()
    config = config_manager.get_config()
    setup_logger(config.get('logging', {}))
    
    # 初始化核心组件
    need_analyzer = NeedAnalyzer(config)
    task_orchestrator = TaskOrchestrator(config)
    cursor_interface = CursorInterface(config)
    progress_monitor = ProgressMonitor(config)
    
    print("✅ 系统组件初始化完成")
    print()
    
    # 2. 需求分析
    print("🧠 第二步：需求分析")
    user_requirement = """
    我想做一个天气预报应用，功能包括：
    1. 显示当前天气情况
    2. 7天天气预报
    3. 城市搜索功能
    4. 用户收藏城市
    5. 天气图标和动画
    
    要求界面美观，支持手机和电脑使用。
    """
    
    print(f"用户需求：{user_requirement.strip()}")
    print()
    print("🔍 正在分析需求...")
    
    analyzed_requirement = await need_analyzer.analyze(user_requirement)
    
    print("📊 需求分析结果：")
    print(f"  - 项目类型：{analyzed_requirement['project_type']}")
    print(f"  - 复杂度：{analyzed_requirement['complexity']}")
    print(f"  - 预估时间：{analyzed_requirement['estimated_hours']} 小时")
    print(f"  - 功能数量：{len(analyzed_requirement['features'])}")
    
    # 显示主要功能
    print("\n  主要功能：")
    for i, feature in enumerate(analyzed_requirement['features'][:3], 1):
        print(f"    {i}. {feature['name']} (优先级: {feature['priority']})")
    
    print("\n  推荐技术栈：")
    tech_stack = analyzed_requirement['tech_stack']
    for category, techs in tech_stack.items():
        if isinstance(techs, list):
            print(f"    - {category}: {', '.join(techs[:2])}")
        else:
            print(f"    - {category}: {techs}")
    
    print()
    
    # 3. 任务分解
    print("⚙️ 第三步：任务分解")
    print("🔄 正在分解开发任务...")
    
    tasks = await task_orchestrator.decompose_tasks(analyzed_requirement)
    
    print(f"📋 任务分解完成，共生成 {len(tasks)} 个任务：")
    print()
    
    for i, task in enumerate(tasks[:5], 1):  # 显示前5个任务
        status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(task['status'], "❓")
        print(f"  {i}. {status_emoji} {task['name']}")
        print(f"     类型：{task['type']} | 优先级：{task['priority']} | 预估：{task['estimated_hours']}h")
        if task.get('dependencies'):
            print(f"     依赖：{', '.join(task['dependencies'])}")
        print()
    
    if len(tasks) > 5:
        print(f"  ... 以及其他 {len(tasks) - 5} 个任务")
        print()
    
    # 4. 展示任务执行（模拟）
    print("🖥️ 第四步：Cursor交互执行")
    print("🚀 开始执行任务...")
    print()
    
    # 模拟执行前几个任务
    demo_workspace = "/tmp/weather_app_demo"
    
    for i, task in enumerate(tasks[:3]):
        print(f"🔄 正在执行：{task['name']}")
        
        # 模拟任务执行
        task_result = await cursor_interface.execute_task(task, demo_workspace)
        
        print(f"  状态：{task_result['status']}")
        print(f"  耗时：{task_result['execution_time']} 秒")
        
        if task_result.get('files_created'):
            print(f"  创建文件：{len(task_result['files_created'])} 个")
        if task_result.get('files_modified'):
            print(f"  修改文件：{len(task_result['files_modified'])} 个")
        
        print()
        
        # 更新任务状态
        task_orchestrator.update_task_status(tasks, task['id'], 'completed')
    
    # 5. 进度总结
    print("📈 第五步：进度总结")
    progress = task_orchestrator.get_project_progress(tasks)
    
    print(f"📊 项目进度：{progress['overall_progress']}%")
    print(f"📋 任务状态：")
    print(f"  - 已完成：{progress['completed_tasks']} / {progress['total_tasks']}")
    print(f"  - 进行中：{progress['in_progress_tasks']}")
    print(f"  - 待执行：{progress['pending_tasks']}")
    print()
    
    # 6. 生成报告
    print("📝 第六步：生成完整报告")
    report = generate_demo_report(analyzed_requirement, tasks, progress)
    
    # 保存报告
    report_file = Path(demo_workspace) / "project_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📄 项目报告已保存：{report_file}")
    print()
    
    print("🎉 === 演示完成！===")
    print()
    print("💡 核心亮点：")
    print("  ✨ 智能需求理解 - 自动分析模糊需求")
    print("  🔧 智能任务分解 - 生成详细开发计划")
    print("  🤖 自动化交互 - 与Cursor无缝协作")
    print("  📊 实时监控 - 跟踪开发进度")
    print("  🌙 夜间开发 - 晚上提需求，早上见成果")
    print()
    print("🚀 这就是Auto Cursor Agent的完整工作流程！")


def generate_demo_report(analyzed_requirement, tasks, progress):
    """生成演示报告"""
    return {
        "project_info": {
            "name": "天气预报应用",
            "type": analyzed_requirement['project_type'],
            "complexity": analyzed_requirement['complexity'],
            "estimated_hours": analyzed_requirement['estimated_hours']
        },
        "requirements": {
            "original": analyzed_requirement['original_requirement'],
            "features_count": len(analyzed_requirement['features']),
            "tech_stack": analyzed_requirement['tech_stack']
        },
        "tasks": {
            "total_tasks": len(tasks),
            "task_breakdown": [
                {
                    "name": task['name'],
                    "type": task['type'],
                    "status": task['status'],
                    "estimated_hours": task['estimated_hours']
                }
                for task in tasks
            ]
        },
        "progress": progress,
        "next_steps": [
            "继续执行剩余任务",
            "集成测试验证",
            "UI优化调整",
            "性能测试",
            "部署发布"
        ],
        "demo_note": "这是Auto Cursor Agent的演示报告，展示了从需求到实现的完整流程"
    }


async def demo_simple_api():
    """演示：简单API服务"""
    
    print("🔌 === Auto Cursor Agent 演示：API服务 ===")
    print()
    
    # 简化版演示
    config_manager = ConfigManager()
    config = config_manager.get_config()
    need_analyzer = NeedAnalyzer(config)
    
    user_requirement = "创建一个用户管理API，包括注册、登录、用户信息查询功能"
    
    print(f"用户需求：{user_requirement}")
    print("🔍 正在分析...")
    
    analyzed = await need_analyzer.analyze(user_requirement)
    
    print(f"✅ 分析完成：")
    print(f"  - 项目类型：{analyzed['project_type']}")
    print(f"  - 复杂度：{analyzed['complexity']}")
    print(f"  - 功能数量：{len(analyzed['features'])}")
    print()


async def main():
    """主演示函数"""
    
    print("🤖 Auto Cursor Agent 完整演示")
    print("=" * 50)
    print()
    
    # 演示选择
    demos = {
        "1": ("天气预报应用（完整演示）", demo_weather_app),
        "2": ("API服务（快速演示）", demo_simple_api)
    }
    
    print("请选择演示场景：")
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    print()
    
    # 如果是脚本运行，默认执行第一个演示
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = "1"  # 默认选择
    
    if choice in demos:
        name, demo_func = demos[choice]
        print(f"🎬 开始演示：{name}")
        print()
        await demo_func()
    else:
        print("❌ 无效选择，执行默认演示")
        await demo_weather_app()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())

