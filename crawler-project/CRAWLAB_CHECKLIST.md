# 🚀 Crawlab部署检查清单

## 📋 部署前检查

### ✅ 文件上传确认
你已经上传的文件夹路径：
```
/Users/winston/Desktop/Gitlab/repository/tk/kiro_tk_DrissionPage_docker/crawlab/crawler-project
```

### 📁 必需文件清单
确保以下文件已上传到Crawlab：

#### 🔧 核心运行文件
- [ ] `crawlab_runner.py` - Crawlab启动器（推荐）
- [ ] `crawlab_simple_runner.py` - 简化版爬虫
- [ ] `spider.json` - Crawlab配置文件
- [ ] `requirements.txt` - 依赖文件

#### 📚 支持文件
- [ ] `config.py` - 基础配置
- [ ] `handlers/` 目录及其文件
- [ ] `utils/` 目录及其文件  
- [ ] `models/` 目录及其文件

#### 📖 文档文件
- [ ] `CRAWLAB_DEPLOYMENT.md` - 部署指南
- [ ] `PROJECT_SUMMARY.md` - 项目总结
- [ ] `CRAWLAB_CHECKLIST.md` - 本检查清单

## 🔧 Crawlab配置检查

### 1. 爬虫基本信息
```json
{
  "name": "电商滑块爬虫",
  "cmd": "python crawlab_runner.py",
  "install_cmd": "pip install -r requirements.txt"
}
```

### 2. 环境变量设置
```json
"env_vars": [
  {"name": "CRAWLAB_MONGO_HOST", "value": "mongo"},
  {"name": "CRAWLAB_MONGO_PORT", "value": "27017"},
  {"name": "CRAWLAB_MONGO_DB", "value": "crawlab_test"},
  {"name": "CHROME_BIN", "value": "/usr/bin/google-chrome"},
  {"name": "DISPLAY", "value": ":99"}
]
```

### 3. 运行参数
- **keywords**: 搜索关键词（如：phone case,data cable）
- **max_pages**: 最大页数（建议：1）
- **headless**: 无头模式（建议：true）

## 🧪 部署测试步骤

### 第1步：依赖安装测试
在Crawlab中运行安装命令：
```bash
pip install -r requirements.txt
```

**预期结果**：
```
Successfully installed DrissionPage ddddocr pymongo requests opencv-python numpy Pillow
```

### 第2步：基础功能测试
运行简单测试：
```bash
python -c "import sys; print('Python版本:', sys.version)"
python -c "from DrissionPage import ChromiumPage; print('DrissionPage导入成功')"
python -c "import ddddocr; print('ddddocr导入成功')"
python -c "import pymongo; print('pymongo导入成功')"
```

### 第3步：爬虫启动测试
运行爬虫启动器：
```bash
python crawlab_runner.py
```

**预期输出**：
```
🚀 Crawlab爬虫启动器
==================================================
🔧 Crawlab环境配置:
  MongoDB: mongodb://mongo:27017
  数据库: crawlab_test
  集合: products
  关键词: phone case
  最大页数: 1
  无头模式: true

🚀 初始化简化版Crawlab爬虫...
✅ 所有依赖导入成功
✅ 数据库连接成功
✅ 浏览器初始化成功
✅ 验证码识别器初始化成功
```

## 🐛 常见问题排查

### 问题1：依赖安装失败
**现象**：pip install失败
**解决**：
1. 检查网络连接
2. 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r crawlab_requirements.txt`
3. 分步安装：先安装基础依赖，再安装复杂依赖

### 问题2：Chrome浏览器启动失败
**现象**：浏览器无法启动
**解决**：
1. 确认环境变量 `CHROME_BIN=/usr/bin/google-chrome`
2. 确认环境变量 `DISPLAY=:99`
3. 检查Docker容器是否支持GUI

### 问题3：MongoDB连接失败
**现象**：数据库连接超时
**解决**：
1. 确认MongoDB服务运行状态
2. 检查网络连接：`ping mongo`
3. 验证连接字符串格式

### 问题4：模块导入失败
**现象**：ModuleNotFoundError
**解决**：
1. 使用 `crawlab_simple_runner.py`（单文件版本）
2. 检查文件上传完整性
3. 确认Python路径设置

## ✅ 成功部署标志

当看到以下输出时，表示部署成功：

```
🎊 爬虫运行完成！
✅ 处理关键词: 1 个
✅ 采集商品: X 个
✅ 浏览器已关闭
✅ 数据库连接已关闭
```

## 📊 数据验证

### MongoDB数据检查
在Crawlab的数据管理界面或MongoDB客户端中执行：

```javascript
// 查看采集的数据
db.products.find().limit(5)

// 统计数据量
db.products.count()

// 按关键词统计
db.products.aggregate([
  {$group: {_id: "$keyword", count: {$sum: 1}}}
])
```

**预期数据结构**：
```json
{
  "_id": "...",
  "product_id": "123456",
  "title": "iPhone 14 Phone Case",
  "keyword": "phone case",
  "scraped_at": "2025-01-31T10:00:00Z",
  "slider_encountered": true,
  "slider_solved": true,
  "source": "tiktok_shop"
}
```

## 🎯 性能监控

### 关键指标
- **采集成功率**: >80%
- **滑块处理成功率**: >70%
- **平均处理时间**: <60秒/关键词
- **内存使用**: <500MB
- **CPU使用**: <50%

### 日志监控
关注以下日志信息：
- `✅ 验证码处理成功`
- `💾 保存商品: XXX`
- `🎊 爬虫运行完成`

## 📞 技术支持

如果遇到问题，请提供：
1. 完整的错误日志
2. 环境变量配置
3. 运行参数设置
4. MongoDB连接状态

## 🎉 部署完成

完成所有检查项后，你的TikTok Shop爬虫就可以在Crawlab环境中稳定运行了！

**记住**：首次运行建议使用较少的关键词和较小的页数进行测试，确认一切正常后再扩大规模。