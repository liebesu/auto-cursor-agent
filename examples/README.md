# 📚 Auto Cursor Agent 使用示例

这个目录包含了Auto Cursor Agent的各种使用示例和演示案例。

## 🎯 演示案例

### 1. 完整工作流程演示

运行完整的开发流程演示：

```bash
# 天气预报应用演示（推荐）
python examples/demo_usage.py 1

# API服务快速演示
python examples/demo_usage.py 2
```

### 2. 典型使用场景

#### 🌐 Web应用开发
```python
from core.need_analyzer import NeedAnalyzer
from core.task_orchestrator import TaskOrchestrator

# 用户需求
requirement = "我想做一个在线博客系统，包括文章发布、评论、用户管理"

# 需求分析
analyzer = NeedAnalyzer(config)
analysis = await analyzer.analyze(requirement)

# 任务分解
orchestrator = TaskOrchestrator(config)
tasks = await orchestrator.decompose_tasks(analysis)
```

#### 📱 移动应用开发
```python
# 移动应用需求
requirement = "开发一个记账app，支持分类记录、图表分析、数据同步"

# 系统会自动识别为mobile_app类型
# 并生成相应的开发任务
```

#### 📊 数据分析项目
```python
# 数据分析需求
requirement = "分析销售数据，生成月度报告和趋势预测图表"

# 自动生成数据处理和可视化任务
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config/config.example.yaml config/config.yaml
# 编辑config.yaml，添加你的OpenAI或Claude API密钥
```

### 2. 基本使用

```python
import asyncio
from main import AutoCursorAgent

async def main():
    # 创建代理实例
    agent = AutoCursorAgent()
    
    # 处理用户需求
    requirement = "你的开发需求"
    workspace = "/path/to/workspace"
    
    result = await agent.process_requirement(requirement, workspace)
    print(f"开发完成：{result}")

# 运行
asyncio.run(main())
```

### 3. 命令行使用

```bash
# 直接运行
python main.py --requirement "我想做个天气app" --workspace "./my_project"

# 指定配置文件
python main.py --config custom_config.yaml --requirement "创建API服务"

# 调试模式
python main.py --debug --requirement "开发需求"
```

## 📋 配置说明

### API密钥配置

在`config/config.yaml`中配置：

```yaml
ai_models:
  openai:
    api_key: "your-openai-api-key"
    model: "gpt-4"
  claude:
    api_key: "your-claude-api-key"
    model: "claude-3-sonnet"

cursor:
  executable_path: "/Applications/Cursor.app/Contents/MacOS/Cursor"
  interaction_mode: "file_based"  # file_based 或 ui_automation
```

### 监控配置

```yaml
monitoring:
  check_interval: 30  # 检查间隔（秒）
  quality_threshold: 0.8  # 质量阈值
  file_patterns:
    - "*.py"
    - "*.js"
    - "*.tsx"
```

## 🌟 高级功能

### 1. 自定义任务模板

```python
# 添加自定义项目类型
from core.task_templates import TaskTemplate

template = TaskTemplate()
template.templates["my_project_type"] = {
    "setup": {
        "name": "自定义初始化",
        "subtasks": ["步骤1", "步骤2"]
    }
}
```

### 2. 扩展AI模型

```python
# 添加新的AI模型
from core.ai_models import BaseAIModel

class CustomAIModel(BaseAIModel):
    async def analyze_requirement(self, requirement: str):
        # 实现自定义分析逻辑
        pass
```

### 3. 自定义监控

```python
# 扩展监控功能
from core.progress_monitor import ProgressMonitor

class CustomMonitor(ProgressMonitor):
    def custom_quality_check(self, files):
        # 实现自定义质量检查
        pass
```

## 🎓 学习路径

1. **基础使用**：运行`demo_usage.py`了解基本流程
2. **配置定制**：修改配置文件适应你的环境
3. **场景实践**：尝试不同类型的项目需求
4. **高级定制**：扩展模板和功能
5. **集成部署**：将系统集成到你的开发流程

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   ```
   解决：检查config.yaml中的API密钥配置
   ```

2. **Cursor路径错误**
   ```
   解决：更新config.yaml中的cursor.executable_path
   ```

3. **依赖缺失**
   ```bash
   pip install -r requirements.txt
   ```

4. **权限问题**
   ```bash
   chmod +x examples/demo_usage.py
   ```

### 调试模式

```bash
# 启用详细日志
python main.py --debug --requirement "你的需求"

# 检查日志文件
tail -f logs/auto_cursor_agent.log
```

## 🤝 贡献

欢迎提交新的示例和改进：

1. Fork项目
2. 创建示例分支
3. 添加你的示例
4. 提交Pull Request

## 📞 支持

如有问题，请：
1. 查看文档和示例
2. 检查Issue列表
3. 提交新Issue
4. 参与Discussion讨论

---

🚀 开始你的AI自动化开发之旅！

