# Crawlab电商爬虫部署指南

## 1. 准备工作

### 1.1 确保Crawlab环境运行正常
```bash
# 检查Crawlab服务状态
docker-compose ps

# 访问Crawlab Web界面
# http://localhost:8080
```

### 1.2 准备爬虫包
- 爬虫包文件: `ecommerce_crawler.zip`
- 包含所有必要的代码和配置文件

## 2. 部署步骤

### 2.1 上传爬虫
1. 登录Crawlab Web界面 (http://localhost:8080)
2. 进入"爬虫"页面
3. 点击"新建爬虫"
4. 选择"上传ZIP文件"
5. 上传 `ecommerce_crawler.zip`
6. 等待上传和解析完成

### 2.2 配置爬虫
1. 爬虫名称: "电商爬虫"
2. 执行命令: `python crawlab_spider.py`
3. 配置参数:
   - keywords: 搜索关键词 (默认: phone case,wireless charger)
   - max_pages: 最大页数 (默认: 1)

### 2.3 环境变量配置
- MONGO_URI: mongodb://mongo:27017
- DATABASE_NAME: crawler_db
- LOG_LEVEL: INFO

## 3. 运行测试

### 3.1 创建任务
1. 进入爬虫详情页
2. 点击"运行"按钮
3. 设置参数:
   - keywords: "数据线"
   - max_pages: 1
4. 点击"开始"

### 3.2 监控执行
1. 在"任务"页面查看任务状态
2. 状态变化: 等待中 → 运行中 → 成功
3. 点击任务详情查看日志

### 3.3 查看结果
1. 在任务详情页查看采集统计
2. 在"结果"页面查看采集的商品数据
3. 检查MongoDB数据库中的数据

## 4. 验证标准

- ✅ 在Crawlab Web界面能看到"电商爬虫"项目
- ✅ 能够成功创建和运行任务
- ✅ 任务状态正常变化: 等待中→运行中→成功
- ✅ 能看到完整的执行日志和采集结果统计
- ✅ 数据正确保存到MongoDB数据库

## 5. 故障排除

### 5.1 常见问题
- 依赖安装失败: 检查requirements.txt
- WebDriver错误: 确保Chrome已安装
- 数据库连接失败: 检查MongoDB服务状态
- 滑块处理失败: 检查ddddocr依赖

### 5.2 日志查看
```bash
# 查看Crawlab容器日志
docker-compose logs -f master
docker-compose logs -f worker

# 查看爬虫执行日志
# 在Crawlab Web界面的任务详情页查看
```

## 6. 性能优化

### 6.1 资源配置
- 内存: 建议至少1GB
- CPU: 建议至少2核
- 磁盘: 建议至少500MB

### 6.2 并发配置
- 单节点建议最多2个并发任务
- 可通过增加Worker节点提高并发能力

## 7. 监控和维护

### 7.1 定期检查
- 每日检查任务执行情况
- 监控数据库存储空间
- 检查日志文件大小

### 7.2 数据备份
```bash
# 备份MongoDB数据
docker exec crawlab_mongo mongodump --out /backup/$(date +%Y%m%d)
```
