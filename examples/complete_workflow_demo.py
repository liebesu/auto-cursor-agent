#!/usr/bin/env python3
"""
完整工作流程演示

展示Auto Cursor Agent的完整开发流程，从需求分析到项目交付
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import AutoCursorAgent
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logger


class CompleteWorkflowDemo:
    """完整工作流程演示"""
    
    def __init__(self):
        self.demo_scenarios = {
            "1": {
                "name": "天气预报Web应用",
                "requirement": """
                我想开发一个现代化的天气预报Web应用，功能包括：
                1. 实时天气显示 - 显示当前温度、湿度、风速等信息
                2. 7天天气预报 - 未来一周的天气趋势
                3. 城市搜索 - 支持全球主要城市搜索
                4. 个人收藏 - 用户可以收藏常用城市
                5. 天气地图 - 显示雷达图和气温分布
                6. 天气提醒 - 恶劣天气自动提醒
                
                技术要求：
                - 响应式设计，支持手机和桌面
                - 现代化UI设计，美观易用
                - 数据来源可靠，更新及时
                - 快速加载，良好的用户体验
                """,
                "workspace": "/tmp/weather_app_demo"
            },
            "2": {
                "name": "任务管理API服务",
                "requirement": """
                开发一个功能完整的任务管理API服务，包括：
                1. 用户管理 - 注册、登录、权限控制
                2. 项目管理 - 创建项目、成员管理、权限分配
                3. 任务管理 - 任务的增删改查、状态跟踪
                4. 标签系统 - 任务分类和过滤
                5. 通知系统 - 任务提醒和状态变更通知
                6. 数据统计 - 项目进度、个人效率统计
                
                技术要求：
                - RESTful API设计
                - JWT身份验证
                - 数据库优化
                - API文档完善
                - 单元测试覆盖
                """,
                "workspace": "/tmp/task_api_demo"
            },
            "3": {
                "name": "数据分析可视化工具",
                "requirement": """
                创建一个数据分析和可视化工具，功能包括：
                1. 数据导入 - 支持CSV、Excel、JSON等格式
                2. 数据清洗 - 缺失值处理、异常值检测
                3. 统计分析 - 描述性统计、相关性分析
                4. 数据可视化 - 多种图表类型、交互式图表
                5. 报告生成 - 自动生成分析报告
                6. 模型训练 - 简单的机器学习模型
                
                技术要求：
                - Python + Streamlit界面
                - Pandas数据处理
                - Plotly/Matplotlib可视化
                - Scikit-learn机器学习
                - 支持大数据量处理
                """,
                "workspace": "/tmp/data_analysis_demo"
            },
            "4": {
                "name": "简单计算器应用",
                "requirement": """
                开发一个功能完善的计算器应用：
                1. 基本运算 - 加减乘除运算
                2. 科学计算 - 三角函数、对数、指数
                3. 历史记录 - 计算历史查看和重用
                4. 内存功能 - 存储和调用数值
                5. 键盘支持 - 支持键盘快捷键
                
                简单快速的演示项目，适合测试完整流程。
                """,
                "workspace": "/tmp/calculator_demo"
            }
        }
    
    async def run_demo(self, scenario_id: str = "1"):
        """运行演示"""
        
        if scenario_id not in self.demo_scenarios:
            print(f"❌ 无效的场景ID: {scenario_id}")
            return
        
        scenario = self.demo_scenarios[scenario_id]
        
        print(f"🚀 开始完整工作流程演示")
        print(f"📋 场景: {scenario['name']}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        try:
            # 1. 初始化Agent
            print("🔧 第一步: 初始化Auto Cursor Agent")
            agent = AutoCursorAgent()
            print("✅ Agent初始化完成")
            print()
            
            # 2. 处理需求
            print("📝 第二步: 开始处理用户需求")
            print("需求内容:")
            print("-" * 40)
            print(scenario['requirement'].strip())
            print("-" * 40)
            print()
            
            print("🔄 正在处理需求...")
            start_time = asyncio.get_event_loop().time()
            
            result = await agent.process_requirement(
                requirement=scenario['requirement'],
                workspace_path=scenario['workspace']
            )
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # 3. 显示结果
            print("🎉 第三步: 处理完成！")
            print(f"⏱️  总耗时: {duration:.1f} 秒")
            print()
            
            # 4. 结果分析
            await self._analyze_results(result, scenario)
            
            # 5. 保存演示报告
            await self._save_demo_report(result, scenario, duration)
            
        except Exception as e:
            print(f"❌ 演示过程出现错误: {e}")
            print("这可能是由于以下原因:")
            print("  - API密钥未配置或无效")
            print("  - 网络连接问题")
            print("  - Cursor可执行文件路径不正确")
            print()
            print("💡 建议:")
            print("  1. 检查config/config.yaml配置")
            print("  2. 确保网络连接正常")
            print("  3. 验证Cursor安装路径")
    
    async def _analyze_results(self, result: dict, scenario: dict):
        """分析演示结果"""
        
        print("📊 演示结果分析:")
        print("-" * 30)
        
        # 基本信息
        print(f"📋 整体状态: {result.get('overall_status', '未知')}")
        
        # 开发阶段结果
        development = result.get('development', {})
        print(f"🔨 开发任务: {development.get('successful_tasks', 0)}/{development.get('total_tasks', 0)} 成功")
        print(f"📈 成功率: {development.get('success_rate', 0):.1%}")
        
        # 优化结果
        optimization = result.get('optimization', {})
        print(f"⚡ 优化次数: {optimization.get('optimizations_performed', 0)}")
        print(f"🎯 质量评分: {optimization.get('final_quality_score', 0):.2f}/1.0")
        
        # 交付状态
        delivery = result.get('delivery', {})
        print(f"📦 交付状态: {delivery.get('status', '未知')}")
        print(f"✅ 验证评分: {delivery.get('validation_score', 0):.2f}/1.0")
        
        # 总结
        summary = result.get('summary', {})
        print(f"🚀 项目就绪: {'是' if summary.get('project_ready', False) else '否'}")
        print(f"🤖 自动化程度: {summary.get('automation_level', '未知')}")
        
        print()
        
        # Auto Cursor Agent特性展示
        aca_info = result.get('auto_cursor_agent', {})
        if aca_info:
            print("🌟 Auto Cursor Agent 核心成就:")
            for achievement in aca_info.get('key_achievements', []):
                print(f"  ✨ {achievement}")
            print()
        
        # 工作空间信息
        workspace_path = scenario['workspace']
        workspace = Path(workspace_path)
        if workspace.exists():
            file_count = len([f for f in workspace.rglob('*') if f.is_file()])
            print(f"📁 生成的文件数量: {file_count}")
            
            # 显示主要文件
            important_files = []
            for pattern in ['*.py', '*.js', '*.ts', '*.html', '*.md', '*.json']:
                important_files.extend(workspace.rglob(pattern))
            
            if important_files:
                print("📄 主要文件:")
                for file_path in important_files[:10]:  # 只显示前10个
                    rel_path = file_path.relative_to(workspace)
                    print(f"  📄 {rel_path}")
                if len(important_files) > 10:
                    print(f"  ... 以及其他 {len(important_files) - 10} 个文件")
            print()
    
    async def _save_demo_report(self, result: dict, scenario: dict, duration: float):
        """保存演示报告"""
        
        # 创建报告目录
        reports_dir = Path("demo_reports")
        reports_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scenario_name = scenario['name'].replace(' ', '_').replace('/', '_')
        report_filename = f"{scenario_name}_{timestamp}.json"
        report_path = reports_dir / report_filename
        
        # 创建详细报告
        demo_report = {
            "demo_info": {
                "scenario_name": scenario['name'],
                "requirement": scenario['requirement'],
                "workspace": scenario['workspace'],
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            },
            "agent_result": result,
            "demo_metadata": {
                "auto_cursor_agent_version": "1.0.0",
                "demo_type": "complete_workflow",
                "automation_achieved": True,
                "manual_intervention_required": result.get('summary', {}).get('manual_review_required', False)
            }
        }
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(demo_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 演示报告已保存: {report_path}")
        print()
    
    def show_menu(self):
        """显示演示菜单"""
        
        print("🤖 Auto Cursor Agent 完整工作流程演示")
        print("=" * 50)
        print()
        print("请选择演示场景:")
        print()
        
        for scenario_id, scenario in self.demo_scenarios.items():
            print(f"  {scenario_id}. {scenario['name']}")
            # 显示需求摘要
            requirement_lines = scenario['requirement'].strip().split('\n')
            summary_line = next((line for line in requirement_lines if line.strip() and not line.strip().startswith('我想')), '')
            if summary_line:
                print(f"     {summary_line.strip()[:50]}...")
            print()
        
        print("  q. 退出")
        print()
    
    async def interactive_demo(self):
        """交互式演示"""
        
        while True:
            self.show_menu()
            
            choice = input("请输入选择 (1-4, q): ").strip().lower()
            
            if choice == 'q':
                print("👋 感谢使用 Auto Cursor Agent 演示！")
                break
            elif choice in self.demo_scenarios:
                print()
                await self.run_demo(choice)
                
                print()
                input("按 Enter 继续...")
                print("\n" + "="*60 + "\n")
            else:
                print("❌ 无效选择，请重试")


async def main():
    """主函数"""
    
    demo = CompleteWorkflowDemo()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        scenario_id = sys.argv[1]
        await demo.run_demo(scenario_id)
    else:
        await demo.interactive_demo()


if __name__ == "__main__":
    print("🚀 Auto Cursor Agent 完整工作流程演示系统")
    print()
    
    # 检查配置
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # 设置日志
        setup_logger(config.get('logging', {}))
        
        print("✅ 系统配置检查通过")
        print()
        
        # 运行演示
        asyncio.run(main())
        
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")
        print()
        print("💡 解决方案:")
        print("1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("2. 配置API密钥: cp config/config.example.yaml config/config.yaml")
        print("3. 检查Cursor安装路径")
        print()
        print("详细信息请查看README.md文档")

