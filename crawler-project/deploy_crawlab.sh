#!/bin/bash
# Crawlab一键部署脚本
# 自动安装系统依赖、Python依赖并运行爬虫

echo "🚀 开始Crawlab环境部署..."
echo "=================================="

# 第一步：安装系统依赖
echo "📦 第一步：安装系统依赖..."
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

# 第一步补充：安装Chrome浏览器
echo "🌐 第一步补充：安装Chrome浏览器..."
bash install_chrome.sh

if [ $? -eq 0 ]; then
    echo "✅ 系统依赖安装成功"
else
    echo "❌ 系统依赖安装失败"
    exit 1
fi

# 第二步：重新安装Python依赖
echo "🐍 第二步：重新安装Python依赖..."
pip uninstall opencv-python -y
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python依赖安装成功"
else
    echo "❌ Python依赖安装失败"
    exit 1
fi

# 第三步：运行环境测试（可选）
echo "🧪 第三步：运行环境测试..."
python test_crawlab_env.py

# 第四步：运行终极修复版爬虫
echo "🎯 第四步：运行终极修复版爬虫..."
python crawlab_ultimate_runner.py

echo "🎉 部署和运行完成！"