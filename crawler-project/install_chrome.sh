#!/bin/bash
# Chrome浏览器安装脚本

echo "🌐 开始安装Chrome浏览器..."

# 检查是否已安装
if command -v google-chrome &> /dev/null; then
    echo "✅ Chrome已安装: $(google-chrome --version)"
    exit 0
fi

# 更新包列表
apt-get update

# 安装必要的依赖
apt-get install -y wget gnupg

# 添加Google Chrome的官方GPG密钥
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# 添加Chrome仓库
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list

# 更新包列表
apt-get update

# 安装Chrome
apt-get install -y google-chrome-stable

# 验证安装
if command -v google-chrome &> /dev/null; then
    echo "✅ Chrome安装成功: $(google-chrome --version)"
    echo "📍 Chrome路径: $(which google-chrome)"
else
    echo "❌ Chrome安装失败"
    exit 1
fi