#!/bin/bash

echo "🛑 停止Crawlab分布式爬虫环境..."

# 停止所有服务
docker-compose down

echo "🧹 清理未使用的Docker资源..."
docker system prune -f

echo "✅ Crawlab环境已停止"