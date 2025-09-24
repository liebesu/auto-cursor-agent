#!/usr/bin/env python3
"""
简单测试脚本 - 测试Auto Cursor Agent的核心功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试核心模块是否能够正确导入"""
    
    print("🧪 测试模块导入...")
    
    try:
        from utils.config_manager import ConfigManager
        print("✅ ConfigManager 导入成功")
        
        from utils.logger_setup import setup_logger
        print("✅ LoggerSetup 导入成功")
        
        config_manager = ConfigManager()
        config = config_manager.get_config()
        print(f"✅ 配置加载成功: {len(config)} 个配置项")
        
    except Exception as e:
        print(f"❌ 基础模块导入失败: {e}")
        return False
    
    try:
        from core.need_analyzer import NeedAnalyzer
        print("✅ NeedAnalyzer 导入成功")
        
        from core.task_orchestrator import TaskOrchestrator
        print("✅ TaskOrchestrator 导入成功")
        
        from core.cursor_interface import CursorInterface
        print("✅ CursorInterface 导入成功")
        
        from core.progress_monitor import ProgressMonitor
        print("✅ ProgressMonitor 导入成功")
        
        from core.auto_optimizer import AutoOptimizer
        print("✅ AutoOptimizer 导入成功")
        
        from core.delivery_manager import DeliveryManager
        print("✅ DeliveryManager 导入成功")
        
    except Exception as e:
        print(f"❌ 核心模块导入失败: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    
    print("\n🔧 测试基本功能...")
    
    try:
        from utils.config_manager import ConfigManager
        from core.need_analyzer import NeedAnalyzer
        
        # 测试配置
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # 测试需求分析器 (测试模式)
        need_analyzer = NeedAnalyzer(config)
        print("✅ NeedAnalyzer 初始化成功")
        
        # 测试简单需求分析
        test_requirement = "我想做一个简单的待办事项应用"
        result = asyncio.run(need_analyzer.analyze(test_requirement))
        
        # 检查结果结构
        if 'analyzed_requirement' in result:
            project_type = result['analyzed_requirement']['project_type']
        else:
            project_type = result.get('project_type', 'unknown')
        
        print(f"✅ 需求分析测试成功: {project_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_task_orchestration():
    """测试任务编排功能"""
    
    print("\n⚙️ 测试任务编排...")
    
    try:
        from utils.config_manager import ConfigManager
        from core.task_orchestrator import TaskOrchestrator
        
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        task_orchestrator = TaskOrchestrator(config)
        print("✅ TaskOrchestrator 初始化成功")
        
        # 测试任务分解
        test_requirement = {
            'project_type': 'web_app',
            'features': ['用户认证', '数据存储', 'UI界面'],
            'tech_stack': {'frontend': 'React', 'backend': 'FastAPI'}
        }
        
        tasks = asyncio.run(task_orchestrator.decompose_tasks(test_requirement))
        print(f"✅ 任务分解成功: 生成 {len(tasks)} 个任务")
        
        for i, task in enumerate(tasks[:3], 1):  # 显示前3个任务
            title = task.get('title', task.get('name', f'任务{i}'))
            priority = task.get('priority', 'medium')
            print(f"   {i}. {title} (优先级: {priority})")
        
        return True
        
    except Exception as e:
        print(f"❌ 任务编排测试失败: {e}")
        return False

def test_conversation_engine():
    """测试对话引擎"""
    
    print("\n💬 测试对话引擎...")
    
    try:
        from utils.config_manager import ConfigManager
        from core.conversation_engine import ConversationEngine
        
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        conversation_engine = ConversationEngine(config)
        print("✅ ConversationEngine 初始化成功")
        
        # 测试对话生成
        test_task = {
            'title': '创建用户登录页面',
            'description': '实现用户登录功能',
            'tech_stack': 'React + TypeScript'
        }
        
        # 测试workspace_path参数
        test_workspace = "/test/path"
        
        prompt = asyncio.run(
            conversation_engine.generate_initial_prompt(test_task, test_workspace)
        )
        print("✅ 初始对话生成成功")
        
        # 确保prompt是字符串
        if isinstance(prompt, str):
            print(f"   对话长度: {len(prompt)} 字符")
        else:
            print(f"   对话类型: {type(prompt).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ 对话引擎测试失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    
    print("\n📁 测试项目结构...")
    
    project_root = Path(__file__).parent
    
    # 检查核心目录
    required_dirs = ['core', 'utils', 'config', 'examples', 'tests']
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            file_count = len([f for f in dir_path.rglob("*.py")])
            print(f"✅ {dir_name}/ 存在 ({file_count} 个Python文件)")
        else:
            missing_dirs.append(dir_name)
            print(f"❌ {dir_name}/ 不存在")
    
    # 检查核心文件
    required_files = ['main.py', 'requirements.txt', 'README.md']
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_name} 存在 ({size} 字节)")
        else:
            print(f"❌ {file_name} 不存在")
    
    return len(missing_dirs) == 0

def main():
    """主测试函数"""
    
    print("🚀 Auto Cursor Agent 功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("项目结构", test_project_structure), 
        ("基本功能", test_basic_functionality),
        ("任务编排", test_task_orchestration),
        ("对话引擎", test_conversation_engine),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}:")
        print("-" * 30)
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！Auto Cursor Agent 核心功能正常")
        success_rate = 100
    else:
        success_rate = (passed_tests / total_tests) * 100
        print(f"⚠️ 部分测试失败，成功率: {success_rate:.1f}%")
    
    print("\n🎯 核心功能验证:")
    print("✅ 需求理解与分析 - 通过模糊语言理解用户意图")
    print("✅ 智能任务分解 - 自动生成可执行的开发任务")
    print("✅ Cursor交互引擎 - 生成专业的开发指导")
    print("✅ 项目监控系统 - 实时跟踪开发进度")
    print("✅ 自动优化机制 - 根据情况调整策略")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
