#!/bin/bash
# Crawlab Docker VNC配置脚本
# 用于在Crawlab环境中启用VNC远程桌面，方便调试滑块验证

echo "🖥️ 开始配置Crawlab VNC环境..."

# 更新包管理器
apt-get update

# 安装VNC服务器和桌面环境
echo "📦 安装VNC服务器和桌面环境..."
apt-get install -y \
    tightvncserver \
    xfce4 \
    xfce4-goodies \
    firefox \
    dbus-x11 \
    x11-xserver-utils

# 安装中文字体支持
apt-get install -y \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    language-pack-zh-hans

# 创建VNC用户目录
mkdir -p ~/.vnc

# 设置VNC密码（默认密码：crawlab123）
echo "🔐 设置VNC密码..."
echo "crawlab123" | vncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# 创建VNC启动脚本
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
EOF

chmod +x ~/.vnc/xstartup

# 创建VNC配置文件
cat > ~/.vnc/config << 'EOF'
session=xfce4
geometry=1920x1080
localhost=no
alwaysshared
EOF

# 启动VNC服务器
echo "🚀 启动VNC服务器..."
vncserver :1 -geometry 1920x1080 -depth 24

# 显示连接信息
echo ""
echo "✅ VNC配置完成！"
echo "=================================="
echo "🔗 VNC连接信息:"
echo "   地址: localhost:5901"
echo "   密码: crawlab123"
echo "   分辨率: 1920x1080"
echo "=================================="
echo ""
echo "📋 使用方法:"
echo "1. 在本地安装VNC客户端（如RealVNC Viewer）"
echo "2. 连接到 localhost:5901"
echo "3. 输入密码: crawlab123"
echo "4. 在VNC桌面中打开终端运行爬虫"
echo ""
echo "🔧 VNC管理命令:"
echo "   启动: vncserver :1"
echo "   停止: vncserver -kill :1"
echo "   查看: vncserver -list"
echo ""

# 设置环境变量
export DISPLAY=:1
echo "export DISPLAY=:1" >> ~/.bashrc

echo "🎉 VNC环境配置完成！现在可以通过VNC客户端连接查看桌面了。"