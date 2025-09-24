#!/bin/bash

# Auto Cursor Agent GitHub 设置脚本
# 使用方法: ./setup_github.sh <github-username> <repository-name>

set -e

echo "🚀 Auto Cursor Agent GitHub 设置脚本"
echo "=================================="

# 检查参数
if [ $# -ne 2 ]; then
    echo "❌ 使用方法: $0 <github-username> <repository-name>"
    echo "   例如: $0 liebesu auto-cursor-agent"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME=$2
GITHUB_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "📋 配置信息:"
echo "   GitHub用户名: ${GITHUB_USERNAME}"
echo "   仓库名称: ${REPO_NAME}"
echo "   仓库URL: ${GITHUB_URL}"
echo ""

# 检查是否在正确的目录
if [ ! -f "main.py" ] || [ ! -f "README.md" ]; then
    echo "❌ 错误: 请在 auto-cursor-agent 项目根目录下运行此脚本"
    exit 1
fi

# 检查Git状态
if [ ! -d ".git" ]; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

echo "🔗 添加GitHub远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin "${GITHUB_URL}"

echo "📤 推送到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 成功! 项目已推送到GitHub:"
echo "   ${GITHUB_URL}"
echo ""
echo "🌐 在浏览器中访问:"
echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
echo ""
echo "📋 后续步骤:"
echo "   1. 在GitHub上设置仓库描述"
echo "   2. 添加Topics标签: ai, cursor, automation, development"
echo "   3. 启用GitHub Pages (可选)"
echo "   4. 设置分支保护规则 (可选)"

