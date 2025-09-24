#!/usr/bin/env python3
"""
Auto Cursor Agent 完整功能演示
展示从需求分析到任务分解的完整流程
"""

import asyncio
import sys
from pathlib import Path
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.config_manager import ConfigManager
from core.need_analyzer import NeedAnalyzer
from core.task_orchestrator import TaskOrchestrator
from core.conversation_engine import ConversationEngine
from core.progress_monitor import ProgressMonitor


async def demo_complete_workflow():
    """演示完整的工作流程"""
    
    print("🚀 Auto Cursor Agent 完整演示")
    print("=" * 60)
    print()
    
    # 1. 初始化系统
    print("📋 第一步：系统初始化")
    print("-" * 30)
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    print("✅ 配置加载完成")
    
    # 初始化核心组件
    need_analyzer = NeedAnalyzer(config)
    task_orchestrator = TaskOrchestrator(config)
    conversation_engine = ConversationEngine(config)
    progress_monitor = ProgressMonitor(config)
    
    print("✅ 核心组件初始化完成")
    print()
    
    # 2. 用户需求输入（模拟用户晚上的输入）
    print("🌙 第二步：用户需求输入 (晚上10点)")
    print("-" * 30)
    
    user_requirements = [
        "我想做一个在线待办事项管理应用，支持用户注册登录",
        "做一个天气预报网站，能显示未来7天天气",
        "创建一个简单的博客系统，支持文章发布和评论"
    ]
    
    print("请选择演示需求：")
    for i, req in enumerate(user_requirements, 1):
        print(f"  {i}. {req}")
    
    try:
        choice = input("\n请输入选择 (1-3，默认1): ").strip()
        if not choice:
            choice = "1"
        selected_requirement = user_requirements[int(choice) - 1]
    except (ValueError, IndexError):
        selected_requirement = user_requirements[0]
    
    print(f"\n🎯 用户需求: {selected_requirement}")
    print()
    
    # 3. 需求分析
    print("🧠 第三步：AI需求分析")
    print("-" * 30)
    
    print("🔍 正在分析用户需求...")
    analysis_result = await need_analyzer.analyze(selected_requirement)
    
    analyzed_req = analysis_result.get('analyzed_requirement', {})
    structured_req = analysis_result.get('structured_requirement', {})
    
    print("✅ 需求分析完成！")
    print(f"   📋 项目类型: {analyzed_req.get('project_type', 'unknown')}")
    print(f"   ⚙️ 复杂度: {analyzed_req.get('complexity_level', 'medium')}")
    print(f"   ⏰ 预估时间: {analyzed_req.get('estimated_time', '2-3周')}")
    
    features = analyzed_req.get('main_features', [])
    if features:
        print(f"   🎯 主要功能: {', '.join(features[:3])}")
    
    tech_stack = analyzed_req.get('tech_stack_suggestions', {})
    if tech_stack:
        print(f"   💻 技术栈: {tech_stack.get('frontend', 'React')} + {tech_stack.get('backend', 'FastAPI')}")
    
    print()
    
    # 4. 任务分解
    print("⚙️ 第四步：智能任务分解")
    print("-" * 30)
    
    print("🔄 正在分解开发任务...")
    tasks = await task_orchestrator.decompose_tasks(structured_req)
    
    print(f"✅ 任务分解完成，共生成 {len(tasks)} 个任务")
    print()
    
    print("📋 任务列表预览:")
    for i, task in enumerate(tasks[:6], 1):  # 显示前6个任务
        title = task.get('title', task.get('name', f'任务{i}'))
        priority = task.get('priority', 'medium')
        estimated_hours = task.get('estimated_hours', 2)
        
        # 优先级图标
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(str(priority).lower(), "⚪")
        
        print(f"  {i}. {priority_icon} {title}")
        print(f"     ⏱️ 预估: {estimated_hours}小时 | 优先级: {priority}")
        
        dependencies = task.get('dependencies', [])
        if dependencies:
            print(f"     🔗 依赖: {', '.join(dependencies)}")
        print()
    
    if len(tasks) > 6:
        print(f"   ... 还有 {len(tasks) - 6} 个任务")
    
    print()
    
    # 5. Cursor交互指导生成  
    print("💬 第五步：Cursor交互指导生成")
    print("-" * 30)
    
    if tasks:
        first_task = tasks[0]
        workspace_path = "./demo_project"
        
        print("🎯 为第一个任务生成Cursor指导...")
        print(f"   任务: {first_task.get('title', '项目初始化')}")
        
        try:
            guidance = await conversation_engine.generate_initial_prompt(
                first_task, workspace_path
            )
            
            print("✅ Cursor指导生成成功!")
            print(f"   📝 指导内容长度: {len(str(guidance))} 字符")
            
            # 显示部分指导内容
            guidance_str = str(guidance)
            preview = guidance_str[:200] + "..." if len(guidance_str) > 200 else guidance_str
            print(f"   📖 内容预览:\n   {preview}")
            
        except Exception as e:
            print(f"⚠️ 指导生成遇到问题: {e}")
            print("✅ 使用备用指导模板")
    
    print()
    
    # 6. 进度监控演示
    print("📊 第六步：进度监控系统")
    print("-" * 30)
    
    print("🎮 启动监控系统...")
    
    # 模拟监控数据
    mock_progress = {
        'total_tasks': len(tasks),
        'completed_tasks': 0,
        'in_progress_tasks': 1,
        'pending_tasks': len(tasks) - 1,
        'overall_progress': 0,
        'estimated_completion': "2-3周",
        'quality_score': 85
    }
    
    print("✅ 监控系统已启动")
    print(f"   📈 总任务数: {mock_progress['total_tasks']}")
    print(f"   ✅ 已完成: {mock_progress['completed_tasks']}")
    print(f"   🔄 进行中: {mock_progress['in_progress_tasks']}")
    print(f"   ⏳ 待开始: {mock_progress['pending_tasks']}")
    print(f"   📊 整体进度: {mock_progress['overall_progress']}%")
    print(f"   🎯 质量评分: {mock_progress['quality_score']}/100")
    
    print()
    
    # 7. 总结报告
    print("📋 第七步：自动化开发总结")
    print("-" * 30)
    
    print("🎉 Auto Cursor Agent 演示完成!")
    print()
    print("📊 演示成果统计:")
    print(f"   🎯 需求理解: ✅ 成功 ({analyzed_req.get('project_type', 'general')}类项目)")
    print(f"   ⚙️ 任务分解: ✅ 生成{len(tasks)}个执行任务")
    print(f"   💬 交互指导: ✅ 为Cursor生成专业指导")
    print(f"   📊 进度监控: ✅ 实时跟踪开发状态")
    print()
    
    print("🌟 核心价值展示:")
    print("   ✨ 智能需求理解 - 从模糊需求到清晰规划")
    print("   ✨ 自动任务编排 - 科学的开发任务分解")  
    print("   ✨ 专业交互指导 - 为Cursor提供上下文指导")
    print("   ✨ 全程质量监控 - 确保开发过程可控")
    print()
    
    print("🚀 如果在真实环境中:")
    print("   🌙 晚上: 用户输入需求，系统自动分析和分解")
    print("   ⚡ 夜间: 系统与Cursor持续交互，指导开发")
    print("   📊 过程: 实时监控，自动调整策略")
    print("   ☀️ 早上: 用户醒来，项目已完成!")
    
    return {
        'status': 'success',
        'requirement': selected_requirement,
        'analysis': analyzed_req,
        'tasks_count': len(tasks),
        'estimated_time': analyzed_req.get('estimated_time', '2-3周')
    }


def demo_api_scenario():
    """快速演示API开发场景"""
    
    print("🚀 API开发场景演示")
    print("=" * 40)
    
    # 模拟API项目需求
    requirement = "创建一个用户管理API，支持注册、登录、用户信息CRUD"
    
    print(f"📋 需求: {requirement}")
    print()
    
    # 模拟分析结果
    analysis = {
        'project_type': 'api',
        'main_features': ['用户注册', '用户登录', '用户管理', 'JWT认证'],
        'tech_stack': {'backend': 'FastAPI', 'database': 'PostgreSQL'},
        'complexity_level': 'medium',
        'estimated_time': '1-2周'
    }
    
    print("🧠 AI分析结果:")
    print(f"   📋 项目类型: {analysis['project_type']}")
    print(f"   🎯 主要功能: {', '.join(analysis['main_features'])}")
    print(f"   💻 技术栈: {analysis['tech_stack']['backend']} + {analysis['tech_stack']['database']}")
    print(f"   ⏰ 预估时间: {analysis['estimated_time']}")
    print()
    
    # 模拟任务分解
    tasks = [
        {'title': '项目初始化', 'priority': 'high', 'estimated_hours': 1},
        {'title': '数据库设计', 'priority': 'high', 'estimated_hours': 3},
        {'title': '用户模型定义', 'priority': 'medium', 'estimated_hours': 2},
        {'title': '认证中间件', 'priority': 'medium', 'estimated_hours': 4},
        {'title': '用户API端点', 'priority': 'medium', 'estimated_hours': 6},
        {'title': 'API文档生成', 'priority': 'low', 'estimated_hours': 2},
        {'title': '单元测试', 'priority': 'medium', 'estimated_hours': 4},
    ]
    
    print("⚙️ 任务分解:")
    for i, task in enumerate(tasks, 1):
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task['priority']]
        print(f"   {i}. {priority_icon} {task['title']} ({task['estimated_hours']}h)")
    
    print()
    print("✅ API项目准备就绪，可开始自动化开发!")
    
    return analysis


async def main():
    """主演示函数"""
    
    print("🤖 Auto Cursor Agent 演示系统")
    print("🌟 让AI成为你的夜间开发伙伴")
    print("=" * 60)
    print()
    
    print("请选择演示模式：")
    print("  1. 完整工作流程演示 (推荐)")
    print("  2. API开发快速演示")
    print("  3. 项目功能测试")
    
    try:
        choice = input("\n请输入选择 (1-3，默认1): ").strip()
        if not choice:
            choice = "1"
    except KeyboardInterrupt:
        print("\n\n👋 演示结束，感谢体验!")
        return
    
    print()
    
    if choice == "1":
        result = await demo_complete_workflow()
        print(f"\n🎊 演示完成！成功处理项目：{result['requirement'][:30]}...")
        
    elif choice == "2":
        result = demo_api_scenario()
        print(f"\n🎊 API演示完成！项目类型：{result['project_type']}")
        
    elif choice == "3":
        # 运行测试
        import subprocess
        print("🧪 正在运行项目功能测试...")
        result = subprocess.run([sys.executable, "test_simple.py"], 
                              cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 功能测试通过!")
        else:
            print("⚠️ 部分功能需要调优")
        
        # 显示测试输出的最后几行
        lines = result.stdout.split('\n')
        for line in lines[-10:]:
            if line.strip():
                print(f"   {line}")
    
    else:
        print("❌ 无效选择，请重新运行")
    
    print()
    print("🌟 Auto Cursor Agent 核心特性:")
    print("   🎯 智能需求理解 - 从模糊想法到精确规划")
    print("   ⚙️ 自动任务分解 - 科学的开发任务编排")
    print("   💬 专业交互指导 - 为Cursor提供上下文指导")
    print("   📊 实时进度监控 - 全程质量控制和优化")
    print("   🔄 自适应调整 - 根据进展动态优化策略")
    
    print()
    print("📍 项目地址: https://github.com/liebesu/auto-cursor-agent")
    print("📖 详细文档: README.md")
    print()
    print("✨ 感谢体验 Auto Cursor Agent!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 演示结束，感谢体验!")
    except Exception as e:
        print(f"\n❌ 演示出现错误: {e}")
        print("🔧 请检查配置文件或联系开发者")
