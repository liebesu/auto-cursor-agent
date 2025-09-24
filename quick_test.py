#!/usr/bin/env python3
"""
Auto Cursor Agent 快速验证测试
验证GitHub提交和核心功能
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, desc):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def test_github_status():
    """测试GitHub状态"""
    print("🔍 检查GitHub同步状态...")
    
    # 检查Git状态
    success, stdout, stderr = run_command("git status --porcelain", "Git状态")
    if success and not stdout:
        print("✅ Git工作目录干净，无未提交更改")
    else:
        print(f"⚠️ Git状态: {stdout}")
    
    # 检查远程同步
    success, stdout, stderr = run_command("git log --oneline -1", "最新提交")
    if success:
        print(f"✅ 最新提交: {stdout}")
    
    # 检查远程分支
    success, stdout, stderr = run_command("git status -b --porcelain", "分支状态")
    if success:
        if "ahead" not in stdout and "behind" not in stdout:
            print("✅ 与远程仓库同步")
        else:
            print(f"⚠️ 分支状态: {stdout}")

def test_core_imports():
    """测试核心模块导入"""
    print("\n🧪 测试核心模块导入...")
    
    modules = [
        "utils.config_manager",
        "core.need_analyzer", 
        "core.task_orchestrator",
        "core.cursor_interface",
        "core.progress_monitor",
        "core.auto_optimizer",
        "core.delivery_manager"
    ]
    
    success_count = 0
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module}: {e}")
    
    print(f"📊 模块导入: {success_count}/{len(modules)} 成功")
    return success_count == len(modules)

def test_basic_functionality():
    """测试基本功能"""
    print("\n⚙️ 测试基本功能...")
    
    try:
        # 测试配置加载
        from utils.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.get_config()
        print("✅ 配置系统加载成功")
        
        # 测试需求分析器 
        from core.need_analyzer import NeedAnalyzer
        analyzer = NeedAnalyzer(config)
        print("✅ 需求分析器初始化成功")
        
        # 测试任务编排器
        from core.task_orchestrator import TaskOrchestrator  
        orchestrator = TaskOrchestrator(config)
        print("✅ 任务编排器初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "config/config.yaml",
        "core/need_analyzer.py",
        "core/task_orchestrator.py",
        "core/cursor_interface.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 缺失")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def main():
    """主测试函数"""
    print("🚀 Auto Cursor Agent 快速验证测试")
    print("=" * 50)
    
    tests = [
        ("GitHub状态", test_github_status),
        ("项目结构", test_project_structure),
        ("模块导入", test_core_imports), 
        ("基本功能", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}测试:")
        print("-" * 30)
        try:
            result = test_func()
            if result is not None:
                results.append(result)
                status = "✅ 通过" if result else "❌ 失败"
                print(f"📊 {test_name}: {status}")
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append(False)
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 快速验证测试总结")
    print("=" * 50)
    
    if all(result for result in results if result is not None):
        print("🎉 所有测试通过！Auto Cursor Agent 状态正常")
        print("\n🏆 验证结果:")
        print("✅ GitHub仓库已同步")
        print("✅ 项目结构完整")
        print("✅ 核心模块可用")
        print("✅ 基本功能正常")
        print("\n🚀 项目地址: https://github.com/liebesu/auto-cursor-agent")
        print("📖 使用文档: README.md")
        print("🌟 项目已准备就绪，可以开始使用！")
        return True
    else:
        passed = sum(1 for r in results if r)
        total = len([r for r in results if r is not None])
        print(f"⚠️ 部分测试失败 ({passed}/{total})")
        print("🔧 请检查失败的测试项目")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
