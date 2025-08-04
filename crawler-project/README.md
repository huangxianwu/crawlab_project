# 🚀 TikTok Shop 爬虫项目

一个完整的TikTok Shop商品爬虫系统，支持智能滑块验证处理、反检测措施和Crawlab平台部署。

## ✨ 核心特性

### 🔍 智能滑块验证处理
- 基于 **ddddocr** 的图像识别技术
- 自动检测和处理TikTok Shop滑块验证
- 人工轨迹模拟，提高成功率

### 🛡️ 反检测措施
- 随机延时（2-5秒可配置）
- User-Agent轮换（7个真实浏览器标识）
- 请求间隔控制
- 指数退避重试机制

### 💾 完整数据存储
- MongoDB数据库集成
- 结构化商品数据存储
- 统计分析功能
- 批量数据处理

### 🐳 Crawlab平台支持
- 完整的Crawlab配置
- 参数化运行支持
- Docker环境适配
- Web界面管理

## 📁 项目结构

```
crawler-project/
├── 🚀 核心运行文件
│   ├── crawlab_fixed_runner.py     # 修复版爬虫（推荐用于Crawlab）
│   ├── run_complete_crawler.py     # 完整版爬虫（功能丰富）
│   ├── crawlab_runner.py           # Crawlab启动器
│   └── crawlab_simple_runner.py    # 简化版爬虫
│
├── 🔧 配置文件
│   ├── spider.json                 # Crawlab爬虫配置
│   ├── requirements.txt            # Python依赖
│   └── config.py                   # 基础配置
│
├── 📦 核心模块
│   ├── handlers/                   # 处理器模块
│   │   ├── slider.py              # 滑块处理
│   │   └── extractor.py           # 数据提取
│   ├── utils/                     # 工具模块
│   │   ├── database.py            # 数据库操作
│   │   ├── logger.py              # 日志系统
│   │   └── anti_detection.py      # 反检测措施
│   └── models/                    # 数据模型
│       └── product.py             # 商品数据结构
│
├── 📚 文档和测试
│   ├── README.md                  # 项目说明
│   ├── CRAWLAB_DEPLOYMENT.md      # 部署指南
│   ├── CRAWLAB_CHECKLIST.md       # 部署检查清单
│   ├── PROJECT_SUMMARY.md         # 项目总结
│   └── test_crawlab_env.py        # 环境测试脚本
│
└── 🧪 示例和测试
    ├── demo_successful_crawler.py  # 成功案例演示
    ├── run_crawler_test.py         # 测试脚本
    └── check_collected_products.py # 数据检查工具
```

## 🚀 快速开始

### 本地开发环境

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **运行完整版爬虫**
   ```bash
   python run_complete_crawler.py
   ```

3. **查看采集结果**
   ```bash
   python check_collected_products.py
   ```

### Crawlab部署

1. **上传项目文件到Crawlab**

2. **配置爬虫参数**
   ```json
   {
     "keywords": "phone case,data cable",
     "max_pages": 1,
     "headless": true
   }
   ```

3. **运行环境测试**
   ```bash
   python test_crawlab_env.py
   ```

4. **启动爬虫**
   ```bash
   python crawlab_fixed_runner.py
   ```

## 🔧 配置说明

### 环境变量
```bash
# MongoDB配置
CRAWLAB_MONGO_HOST=mongo
CRAWLAB_MONGO_PORT=27017
CRAWLAB_MONGO_DB=crawlab_test

# 浏览器配置
CHROME_BIN=/usr/bin/google-chrome
DISPLAY=:99

# 运行参数
keywords=phone case
max_pages=1
headless=true
```

### 依赖要求
- Python 3.8+
- DrissionPage >= 4.1.0
- ddddocr >= 1.4.7
- pymongo >= 4.6.0
- opencv-python-headless >= 4.8.0

## 📊 功能演示

### 滑块验证处理
```
🧩 检测到验证码，正在处理...
🎯 识别到滑块位置: 342
📐 计算的实际滑动距离: 203.65
✅ 验证码处理成功
```

### 数据采集结果
```
🎊 爬虫运行完成！
✅ 处理关键词: 2 个
✅ 采集商品: 15 个
✅ 数据库总商品: 456 条
```

### 数据库存储格式
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

## 🐛 故障排除

### 常见问题

1. **OpenGL库缺失**
   ```bash
   apt-get install -y libgl1-mesa-glx libglib2.0-0
   ```

2. **模块导入失败**
   - 使用 `crawlab_fixed_runner.py`（推荐）
   - 检查文件上传完整性

3. **滑块处理失败**
   - 检查ddddocr安装状态
   - 调整拖拽距离计算参数

4. **数据库连接失败**
   - 验证MongoDB服务状态
   - 检查连接字符串格式

## 📈 性能指标

- **采集效率**: 平均26秒/关键词
- **滑块处理**: 平均3-5秒识别和处理
- **成功率**: >80%（正常网络环境）
- **内存使用**: <500MB
- **CPU使用**: <50%

## 🔮 扩展功能

### 已实现
- ✅ 智能滑块验证处理
- ✅ 反检测措施
- ✅ 数据存储和统计
- ✅ Crawlab平台集成

### 计划中
- [ ] 代理IP池集成
- [ ] 多电商平台支持
- [ ] 实时监控面板
- [ ] 数据分析和可视化
- [ ] API接口服务

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关网站的robots.txt和服务条款。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 技术支持

如果在使用过程中遇到问题，请：

1. 查看 [部署指南](CRAWLAB_DEPLOYMENT.md)
2. 运行 [环境测试脚本](test_crawlab_env.py)
3. 检查 [故障排除清单](CRAWLAB_CHECKLIST.md)

---

**⭐ 如果这个项目对你有帮助，请给个Star支持一下！**