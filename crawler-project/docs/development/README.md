# 电商爬虫系统

基于Crawlab的分布式电商爬虫系统MVP版本，支持滑块验证自动处理和批量数据采集。

## 项目特性

- 🚀 基于Crawlab的分布式架构
- 🤖 智能滑块验证处理（基于ddddocr）
- 📊 MongoDB数据存储
- 🔄 自动重试和错误处理
- 📝 完整的日志记录
- ⚙️ 灵活的配置管理

## 项目结构

```
crawler-project/
├── main.py              # 主入口文件
├── config.py            # 配置管理
├── models/              # 数据模型
│   ├── __init__.py
│   └── product.py       # 商品数据模型
├── utils/               # 工具类
│   ├── __init__.py
│   ├── database.py      # 数据库操作
│   └── logger.py        # 日志工具
├── handlers/            # 处理器
│   └── __init__.py
├── requirements.txt     # 依赖包
├── README.md           # 项目说明
└── logs/               # 日志目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

确保MongoDB服务正在运行：

```bash
# 使用Docker启动MongoDB (如果没有本地安装)
docker run -d --name mongodb -p 27017:27017 mongo:4.4
```

### 3. 运行系统

```bash
python main.py
```

## 配置说明

主要配置项在 `config.py` 文件中：

### 目标网站配置
- `TARGET_URL`: 目标电商网站URL
- `SEARCH_INPUT_SELECTOR`: 搜索输入框选择器
- `PRODUCT_TITLE_SELECTOR`: 商品标题选择器

### 爬虫行为配置
- `MIN_DELAY` / `MAX_DELAY`: 请求延时范围
- `MAX_RETRY`: 最大重试次数
- `PAGE_LOAD_TIMEOUT`: 页面加载超时时间

### 数据库配置
- `MONGO_URI`: MongoDB连接URI
- `DATABASE_NAME`: 数据库名称
- `COLLECTION_NAME`: 集合名称

### 日志配置
- `LOG_LEVEL`: 日志级别
- `LOG_DIR`: 日志目录
- `LOG_FILE`: 日志文件名

## 环境变量

可以通过环境变量覆盖配置：

```bash
export MONGO_URI="mongodb://localhost:27017"
export DATABASE_NAME="crawler_db"
export LOG_LEVEL="DEBUG"
export DEBUG_MODE="true"
```

## 数据模型

### ProductData

商品数据模型包含以下字段：

- `keyword`: 搜索关键词
- `title`: 商品标题
- `scraped_at`: 采集时间
- `slider_encountered`: 是否遇到滑块
- `slider_solved`: 滑块是否解决成功

## 测试

### 数据库功能测试

```bash
python test_database.py
```

### 数据库功能演示

```bash
python demo_database.py
```

## 开发指南

### 添加新的数据字段

1. 修改 `models/product.py` 中的 `ProductData` 类
2. 更新 `to_dict()` 和 `from_dict()` 方法
3. 运行测试确保兼容性

### 添加新的处理器

1. 在 `handlers/` 目录下创建新的处理器文件
2. 继承基础处理器类（如果有）
3. 实现必要的接口方法
4. 在主流程中集成新处理器

### 自定义配置

1. 在 `config.py` 中添加新的配置项
2. 设置合理的默认值
3. 支持环境变量覆盖
4. 在 `validate_config()` 中添加验证逻辑

## 日志说明

系统使用分层日志记录：

- **INFO**: 正常操作信息
- **WARNING**: 警告信息（如滑块检测）
- **ERROR**: 错误信息
- **DEBUG**: 调试信息（仅在DEBUG模式下）

日志文件位置：`logs/crawler.log`

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MongoDB服务是否启动
   - 验证连接URI是否正确
   - 检查网络连接

2. **依赖安装失败**
   - 更新pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`

3. **日志文件权限问题**
   - 确保logs目录有写权限
   - 检查磁盘空间是否充足

## 版本历史

- **v1.0-mvp**: MVP版本，基础功能实现
  - 数据模型和存储
  - 配置管理
  - 日志记录
  - 项目结构搭建

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目仓库: https://github.com/huangxianwu/crawlab
- 问题反馈: 通过GitHub Issues

---

**注意**: 本项目仅用于学习和研究目的，请遵守相关网站的robots.txt协议和使用条款。