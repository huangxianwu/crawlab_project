#!/bin/bash

echo "🚀 启动Crawlab分布式爬虫环境..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "📦 拉取最新的Crawlab镜像..."
docker-compose pull

echo "🔧 启动Crawlab服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "🔍 检查服务状态..."
docker-compose ps

echo ""
echo "✅ Crawlab环境启动完成！"
echo ""
echo "📊 访问地址："
echo "   Crawlab Web界面: http://localhost:8080"
echo "   MongoDB: localhost:27017"
echo "   Redis: localhost:6379"
echo ""
echo "🔑 默认登录信息："
echo "   用户名: admin"
echo "   密码: admin"
echo ""
echo "📝 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""