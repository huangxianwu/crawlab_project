# 电商爬虫项目部署文档

## 项目概述
基于Crawlab的分布式电商爬虫系统，支持滑块验证自动处理和批量数据采集。

## 系统要求

### 硬件要求
- **开发环境**: 4核CPU, 8GB内存, 20GB硬盘
- **生产环境**: 8核CPU, 16GB内存, 100GB硬盘
- **网络**: 稳定的互联网连接

### 软件要求
- Docker >= 20.10.0
- Docker Compose >= 2.0.0
- Git >= 2.0.0

## 快速部署指南

### 1. 克隆项目
```bash
git clone https://github.com/huangxianwu/crawlab.git
cd crawlab
```

### 2. 启动服务
```bash
# 启动Crawlab环境
./start-crawlab.sh

# 或者手动启动
docker-compose up -d
```

### 3. 访问系统
- **Web界面**: http://localhost:8080
- **默认账号**: admin / admin
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

## 任务完成记录

### ✅ 任务1: 搭建Crawlab开发环境 (已完成)

**完成时间**: 2025-01-31

**部署步骤**:
1. 创建Docker Compose配置文件
2. 配置Crawlab Master和Worker节点
3. 集成MongoDB和Redis服务
4. 创建启动和停止脚本

**生产环境部署命令**:
```bash
# 1. 安装Docker和Docker Compose (CentOS/RHEL)
sudo yum update -y
sudo yum install -y docker docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# 2. 克隆项目
git clone https://github.com/huangxianwu/crawlab.git
cd crawlab

# 3. 启动服务
chmod +x start-crawlab.sh stop-crawlab.sh
./start-crawlab.sh

# 4. 验证部署
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
docker-compose ps
```

**验证清单**:
- [ ] 浏览器访问 http://localhost:8080 显示Crawlab登录界面
- [ ] 使用 admin/admin 成功登录
- [ ] 在"节点"页面看到Master和Worker节点状态为"在线"
- [ ] MongoDB连接正常 (端口27017可访问)
- [ ] Redis连接正常 (端口6379可访问)

**配置文件**:
- `docker-compose.yml`: Docker服务编排配置
- `start-crawlab.sh`: 启动脚本
- `stop-crawlab.sh`: 停止脚本

---

### 🔄 任务2: 创建简化的数据模型和存储 (待完成)

**预期部署步骤**:
1. 创建MongoDB数据模型
2. 实现基础CRUD操作
3. 测试数据库连接和写入

**生产环境部署命令**:
```bash
# 待任务完成后更新...
```

---

### 🔄 任务3: 创建基础爬虫项目结构 (待完成)

**预期部署步骤**:
1. 创建Python项目结构
2. 配置依赖包
3. 实现配置管理和日志

**生产环境部署命令**:
```bash
# 待任务完成后更新...
```

---

### 🔄 任务4: 实现基础WebDriver和搜索功能 (待完成)

**预期部署步骤**:
1. 安装Chrome和ChromeDriver
2. 配置Selenium WebDriver
3. 实现商品搜索功能

**生产环境部署命令**:
```bash
# 待任务完成后更新...
```

---

### 🔄 任务5: 实现滑块检测和处理核心逻辑 (待完成)

**预期部署步骤**:
1. 安装ddddocr和相关依赖
2. 实现滑块识别算法
3. 集成滑块处理流程

**生产环境部署命令**:
```bash
# 待任务完成后更新...
```

---

## 生产环境部署完整流程

### 服务器准备
```bash
# 1. 更新系统
sudo yum update -y

# 2. 安装必要软件
sudo yum install -y git curl wget

# 3. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 4. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. 验证安装
docker --version
docker-compose --version
```

### 项目部署
```bash
# 1. 克隆项目
git clone https://github.com/huangxianwu/crawlab.git
cd crawlab

# 2. 配置环境变量 (生产环境)
cp docker-compose.yml docker-compose.prod.yml
# 编辑生产配置...

# 3. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 验证部署
docker-compose ps
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080
```

### 监控和维护
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 更新服务
git pull origin main
docker-compose pull
docker-compose up -d

# 备份数据
docker exec crawlab_mongo mongodump --out /backup/$(date +%Y%m%d)

# 清理资源
docker system prune -f
```

## 故障排除

### 常见问题

**1. Docker服务无法启动**
```bash
# 检查Docker状态
sudo systemctl status docker

# 重启Docker
sudo systemctl restart docker
```

**2. 端口冲突**
```bash
# 检查端口占用
netstat -tulpn | grep :8080

# 修改docker-compose.yml中的端口映射
```

**3. 内存不足**
```bash
# 检查内存使用
free -h
docker stats

# 调整Docker内存限制
```

**4. 网络连接问题**
```bash
# 检查网络连接
docker network ls
docker network inspect kiro_crawlab_default
```

## 安全配置

### 生产环境安全建议
1. 修改默认密码
2. 配置防火墙规则
3. 启用HTTPS
4. 定期备份数据
5. 监控系统资源

### 防火墙配置
```bash
# 开放必要端口
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

## 性能优化

### 资源配置建议
- **小规模** (1-5万关键词/天): 4核8GB, 2个Worker
- **中规模** (5-20万关键词/天): 8核16GB, 5个Worker  
- **大规模** (20万+关键词/天): 16核32GB, 10个Worker

### 扩展Worker节点
```bash
# 在新服务器上启动Worker
docker run -d \
  --name crawlab_worker_2 \
  -e CRAWLAB_NODE_MASTER=N \
  -e CRAWLAB_GRPC_ADDRESS=master_ip:9666 \
  -e CRAWLAB_MONGO_HOST=mongo_ip:27017 \
  crawlabteam/crawlab:0.6.0
```

---

**文档版本**: v1.0  
**最后更新**: 2025-01-31  
**维护者**: 项目开发团队