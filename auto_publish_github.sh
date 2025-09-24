#!/bin/bash

# Auto Cursor Agent 自动创建GitHub仓库并推送脚本
# 使用方法: ./auto_publish_github.sh [repository-name]

set -e

echo "🚀 Auto Cursor Agent 自动GitHub发布脚本"
echo "========================================="

# 默认仓库名
DEFAULT_REPO_NAME="auto-cursor-agent"
REPO_NAME=${1:-$DEFAULT_REPO_NAME}

echo "📋 发布配置:"
echo "   仓库名称: ${REPO_NAME}"
echo ""

# 检查是否在正确的目录
if [ ! -f "main.py" ] || [ ! -f "README.md" ]; then
    echo "❌ 错误: 请在 auto-cursor-agent 项目根目录下运行此脚本"
    exit 1
fi

# 检查GitHub CLI是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI 未安装，正在安装..."
    
    # 根据操作系统安装GitHub CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            echo "📦 使用Homebrew安装GitHub CLI..."
            brew install gh
        else
            echo "❌ 请先安装Homebrew或手动安装GitHub CLI"
            echo "   Homebrew: https://brew.sh"
            echo "   GitHub CLI: https://cli.github.com"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "📦 使用apt安装GitHub CLI..."
        sudo apt update
        sudo apt install gh -y
    else
        echo "❌ 不支持的操作系统，请手动安装GitHub CLI: https://cli.github.com"
        exit 1
    fi
fi

# 检查GitHub CLI登录状态
echo "🔐 检查GitHub CLI登录状态..."
if ! gh auth status &> /dev/null; then
    echo "⚠️  未登录GitHub CLI，正在启动登录流程..."
    gh auth login
else
    echo "✅ 已登录GitHub CLI"
fi

# 获取GitHub用户名
GITHUB_USERNAME=$(gh api user --jq '.login')
echo "👤 GitHub用户名: ${GITHUB_USERNAME}"

# 检查仓库是否已存在
echo "🔍 检查仓库是否已存在..."
if gh repo view "${GITHUB_USERNAME}/${REPO_NAME}" &> /dev/null; then
    echo "⚠️  仓库 ${GITHUB_USERNAME}/${REPO_NAME} 已存在"
    read -p "是否要删除现有仓库并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  删除现有仓库..."
        gh repo delete "${GITHUB_USERNAME}/${REPO_NAME}" --confirm
    else
        echo "❌ 操作已取消"
        exit 1
    fi
fi

# 初始化Git仓库（如果未初始化）
if [ ! -d ".git" ]; then
    echo "🔧 初始化Git仓库..."
    git init
    git add .
    git commit -m "🚀 Initial commit: Auto Cursor Agent - 自动化Cursor交互开发代理"
fi

# 创建GitHub仓库
echo "🆕 创建GitHub仓库..."
gh repo create "${REPO_NAME}" \
    --public \
    --description "🤖 自动化Cursor交互开发代理 | 智能需求理解 + 自动化开发 + 实时监控 | AI驱动的夜间开发神器" \
    --source=. \
    --remote=origin \
    --push

# 设置仓库主题标签
echo "🏷️  设置仓库标签..."
gh repo edit "${GITHUB_USERNAME}/${REPO_NAME}" \
    --add-topic "ai" \
    --add-topic "cursor" \
    --add-topic "automation" \
    --add-topic "development" \
    --add-topic "agent" \
    --add-topic "coding-assistant" \
    --add-topic "python" \
    --add-topic "artificial-intelligence" \
    --add-topic "developer-tools" \
    --add-topic "automatic-programming"

# 启用Issues和Discussions
echo "⚙️  配置仓库功能..."
gh repo edit "${GITHUB_USERNAME}/${REPO_NAME}" \
    --enable-issues \
    --enable-discussions \
    --enable-wiki

# 创建第一个Release
echo "🎉 创建初始Release..."
gh release create "v0.1.0" \
    --title "🚀 Auto Cursor Agent v0.1.0 - 初始版本" \
    --notes "## 🎯 首个公开版本

### ✨ 核心特性
- 🧠 **智能需求理解**: 自动分析用户的模糊需求，生成详细开发计划
- 🤖 **自动化交互**: 与Cursor进行多轮对话，指导完整开发过程  
- 📊 **实时监控**: 监控开发进度和代码质量，自动调整策略
- 🔄 **反馈优化**: 基于结果持续学习和优化交互模式
- 🌙 **夜间开发**: 用户晚上提需求，早上起床发现已完美实现

### 🏗️ 架构设计
- 模块化设计，易于扩展
- 完整的配置管理系统
- 详细的日志记录和监控
- 支持多种AI模型

### 📋 使用场景
- Web应用开发
- 移动应用开发  
- 数据分析工具
- API服务开发

### 🚀 快速开始
\`\`\`bash
pip install -r requirements.txt
cp config/config.example.yaml config/config.yaml
python main.py --requirement \"你的开发需求\"
\`\`\`

---
**让AI成为你的夜间开发伙伴！** 🌟" \
    --prerelease

echo ""
echo "🎉 成功! 项目已自动创建并发布到GitHub:"
echo "   📍 仓库地址: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo "   🏷️  Release: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}/releases/tag/v0.1.0"
echo ""
echo "📋 后续建议:"
echo "   1. ⭐ Star你自己的项目来增加可见性"
echo "   2. 📢 在社交媒体分享你的项目"
echo "   3. 📝 写一篇技术博客介绍项目"
echo "   4. 🚀 提交到awesome-ai-tools等列表"
echo "   5. 💬 在相关技术社区分享"
echo ""
echo "🌟 项目标签已设置，Release已创建，开始获得关注吧！"
