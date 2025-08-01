# Implementation Plan - MVP核心流程验证

## Git仓库管理

**目标仓库**: https://github.com/huangxianwu/crawlab.git

**提交规范**: 遵循 `.kiro/steering/crawler-development-rules.md` 中的Git提交规范
- 每个任务完成后必须提交代码到GitHub
- 使用规范的提交信息格式
- **每个任务完成后必须更新 DEPLOYMENT.md 文档**，记录部署步骤和验证清单
- MVP完成后创建版本标签

## Phase 1: 基础环境和数据模型

- [x] 1. 搭建Crawlab开发环境
  - 安装Docker和Docker Compose
  - 部署Crawlab主节点和工作节点
  - 配置MongoDB数据存储
  - 验证Crawlab Web界面可正常访问
  - _Requirements: 3.1, 3.2_
  
  **验证标准**:
  - ✅ 浏览器访问 http://localhost:8080 显示Crawlab登录界面
  - ✅ 成功登录后看到主控制台，显示Master和Worker节点状态为"在线"
  - ✅ 在"节点"页面能看到至少1个Master节点和1个Worker节点
  - ✅ MongoDB连接正常，可以在数据库中看到crawlab相关的集合
  
  **Git提交要求**:
  - 创建项目仓库并初始化：`git init && git remote add origin https://github.com/huangxianwu/crawlab.git`
  - 提交Docker配置文件：`git add docker-compose.yml && git commit -m "feat(env): 搭建Crawlab开发环境"`
  - 推送到远程仓库：`git push -u origin main`

- [x] 2. 创建简化的数据模型和存储
  - 定义商品标题数据结构（仅包含：关键词、标题、采集时间）
  - 实现MongoDB连接和基础CRUD操作
  - 创建简单的数据插入和查询方法
  - 测试数据库连接和写入功能
  - _Requirements: 1.3_
  
  **验证标准**:
  - ✅ 运行测试脚本，成功连接到MongoDB数据库
  - ✅ 插入一条测试数据：{"keyword": "测试", "title": "测试商品标题", "scraped_at": "2025-01-31T10:00:00Z"}
  - ✅ 查询数据库，能够正确返回刚插入的测试数据
  - ✅ 在MongoDB Compass或命令行中能看到新创建的products集合和测试数据
  
  **Git提交要求**:
  - 提交数据模型和数据库工具：`git add models/ utils/database.py`
  - 提交信息：`git commit -m "feat(data): 实现商品数据模型和MongoDB存储功能"`
  - 推送更新：`git push origin main`

- [ ] 3. 创建基础爬虫项目结构
  - 创建Python爬虫脚本框架
  - 配置requirements.txt（selenium, pymongo, requests等）
  - 实现基础配置管理（目标网站URL、选择器等）
  - 创建简单的日志记录功能
  - _Requirements: 4.1, 4.2_
  
  **验证标准**:
  - ✅ 项目目录结构清晰，包含main.py、config.py、requirements.txt等文件
  - ✅ 运行 `pip install -r requirements.txt` 成功安装所有依赖
  - ✅ 运行基础脚本，能够输出配置信息（目标网站URL、数据库连接等）
  - ✅ 日志文件正常生成，包含时间戳和基本的运行信息
  
  **Git提交要求**:
  - 提交项目基础结构：`git add main.py config.py requirements.txt utils/logger.py README.md`
  - 提交信息：`git commit -m "feat(structure): 创建爬虫项目基础结构和配置管理"`
  - 推送更新：`git push origin main`

## Phase 2: 核心MVP流程实现

- [ ] 4. 实现基础WebDriver和搜索功能
  - 配置Chrome浏览器（显示模式，便于调试滑块）
  - 实现关键词搜索页面导航
  - 编写商品标题提取器（仅提取标题文本）
  - 实现基础的页面等待和错误处理
  - _Requirements: 1.1, 1.2_
  
  **验证标准**:
  - ✅ 运行脚本后，Chrome浏览器自动打开并导航到目标电商网站
  - ✅ 输入关键词"手机壳"，能够自动搜索并跳转到搜索结果页面
  - ✅ 控制台输出至少5个商品标题，格式如："苹果iPhone14手机壳透明防摔"
  - ✅ 页面加载等待正常工作，不会因为页面未加载完成而报错
  
  **Git提交要求**:
  - 提交WebDriver和数据提取功能：`git add utils/webdriver.py handlers/extractor.py`
  - 提交信息：`git commit -m "feat(crawler): 实现基础WebDriver管理和商品搜索功能"`
  - 推送更新：`git push origin main`

- [ ] 5. 实现滑块检测和处理核心逻辑 (基于TikTok项目经验)
  - 安装ddddocr和相关依赖包 (ddddocr, opencv-python, numpy)
  - 实现多重滑块检测策略 (HTML检查、元素检查、图片检查)
  - 集成ddddocr滑块图像识别算法
  - 开发人工滑动轨迹生成算法 (加速-减速模式)
  - 实现带重试机制的滑块处理流程 (最多3次重试)
  - 添加随机滑动备用方案
  - _Requirements: 2.1, 2.2_
  
  **验证标准**:
  - ✅ 安装依赖后运行 `python -c "import ddddocr; print('ddddocr安装成功')"` 成功
  - ✅ 手动触发滑块验证页面，脚本能够自动识别并输出"检测到滑块验证"
  - ✅ 控制台输出ddddocr识别结果，如"识别到滑块位置: target_x=150"
  - ✅ 观察浏览器中滑块自动移动，轨迹呈现加速-减速的人工特征
  - ✅ 滑块验证成功后，页面正常跳转，输出"滑块验证成功"
  - ✅ 验证失败时能够自动重试，最多3次后输出"滑块处理失败"
  
  **Git提交要求**:
  - 提交滑块处理核心功能：`git add handlers/slider.py requirements.txt`
  - 提交信息：`git commit -m "feat(slider): 基于ddddocr实现智能滑块验证处理"`
  - 推送更新：`git push origin main`

- [x] 6. 集成完整的MVP流程
  - 实现：搜索→采集标题→检测滑块→处理滑块→继续采集的完整流程
  - 添加数据保存到MongoDB的功能
  - 实现简单的关键词输入接口（命令行或配置文件）
  - 测试完整流程的可行性
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2_
  
  **验证标准**:
  - ✅ 输入关键词"手机壳"，完整流程自动执行：搜索→采集→遇到滑块→自动处理→继续采集
  - ✅ 控制台输出完整的执行日志，包括每个步骤的状态
  - ✅ 查询MongoDB数据库，能看到采集的商品标题数据，包含滑块处理记录
  - ✅ 整个流程能够在5分钟内完成，采集到至少10个商品标题
  
  **Git提交要求**:
  - 提交完整MVP流程：`git add main.py -u`
  - 提交信息：`git commit -m "feat(mvp): 集成完整的爬虫MVP流程，支持滑块自动处理"`
  - 推送更新：`git push origin main`

## Phase 3: Crawlab集成和优化

- [ ] 7. 集成Crawlab任务调度
  - 将Python爬虫脚本部署到Crawlab
  - 配置爬虫任务参数（关键词输入）
  - 实现任务执行状态监控
  - 测试通过Crawlab Web界面运行爬虫
  - _Requirements: 3.1, 3.2_
  
  **验证标准**:
  - ✅ 在Crawlab Web界面能看到新创建的"电商爬虫"项目
  - ✅ 点击"运行"按钮，在参数中输入关键词"数据线"，任务成功启动
  - ✅ 在"任务"页面能看到任务执行状态从"等待中"→"运行中"→"成功"
  - ✅ 点击任务详情，能看到完整的执行日志和采集结果统计
  
  **Git提交要求**:
  - 提交Crawlab集成配置：`git add crawlab_spider.py spider.json`
  - 提交信息：`git commit -m "feat(crawlab): 集成Crawlab任务调度和Web界面管理"`
  - 推送更新：`git push origin main`

- [ ] 8. 添加基础的反检测措施
  - 添加随机延时（2-5秒）
  - 设置真实的User-Agent
  - 实现简单的请求间隔控制
  - 添加基础的错误重试机制（暂不包含代理IP切换）
  - _Requirements: 2.4, 2.3_
  
  **验证标准**:
  - ✅ 观察爬虫执行过程，每个操作之间有2-5秒的随机延时
  - ✅ 检查浏览器开发者工具，User-Agent显示为真实的Chrome浏览器标识
  - ✅ 模拟网络错误，脚本能够自动重试3次，并在日志中记录重试过程
  - ✅ 连续运行30分钟，系统稳定运行，没有被目标网站封禁
  
  **Git提交要求**:
  - 提交反检测优化：`git add utils/anti_detection.py -u`
  - 提交信息：`git commit -m "feat(anti-detect): 添加基础反检测措施和错误重试机制"`
  - 推送更新：`git push origin main`

- [ ] 9. 完善数据存储和查看
  - 优化数据库存储结构
  - 实现采集结果的查询和导出功能
  - 添加采集统计信息（成功/失败数量）
  - 通过Crawlab界面查看采集结果
  - _Requirements: 1.3, 3.3_
  
  **验证标准**:
  - ✅ 在Crawlab的"数据"页面能看到采集的商品数据，包含关键词、标题、时间等字段
  - ✅ 能够按关键词筛选数据，导出CSV格式的采集结果
  - ✅ 在任务详情页面能看到统计信息：成功采集X条，失败Y条，滑块处理成功率Z%
  - ✅ 数据库中的数据结构清晰，支持后续的数据分析和处理
  
  **Git提交要求**:
  - 提交数据管理优化：`git add utils/data_manager.py utils/statistics.py -u`
  - 提交信息：`git commit -m "feat(data): 完善数据存储管理和统计功能"`
  - 推送更新：`git push origin main`
  - 创建MVP完成标签：`git tag -a v1.0-mvp -m "MVP版本完成：支持关键词搜索、滑块处理、数据采集"`
  - 推送标签：`git push origin v1.0-mvp`

## MVP验证目标

完成前9个任务后，系统将实现以下核心验证流程：

### 渐进式开发验证策略

**每个任务完成后的验证原则**:
1. **可视化验证**: 能够通过浏览器、界面或日志直观看到结果
2. **功能性验证**: 核心功能按预期工作，输出符合需求
3. **数据验证**: 相关数据正确存储和展示
4. **稳定性验证**: 功能能够重复执行，结果一致

**验证失败时的处理**:
- 立即停止后续任务开发
- 分析问题根因，调整当前任务实现
- 重新验证通过后再继续下一个任务
- 避免错误积累，确保每一步都是可靠的基础

### 最终MVP效果演示
```
1. 输入关键词："手机壳"
2. 自动打开浏览器，搜索商品
3. 开始采集商品标题：
   - "苹果iPhone14手机壳透明防摔"
   - "华为mate50手机壳硅胶软壳"
   - ...
4. 遇到滑块验证 → 自动识别并处理
5. 滑块验证成功后继续采集：
   - "小米13手机壳全包边防摔"
   - "OPPO手机壳个性创意"
6. 所有标题保存到MongoDB数据库
7. 通过Crawlab界面查看采集结果
```

### 数据库存储格式
```json
{
  "_id": "...",
  "keyword": "手机壳",
  "title": "苹果iPhone14手机壳透明防摔",
  "scraped_at": "2025-01-31T10:30:00Z",
  "slider_encountered": true,
  "slider_solved": true
}
```

### 成功标准
- ✅ 能够自动搜索关键词
- ✅ 能够提取商品标题
- ✅ 能够识别滑块验证
- ✅ 能够自动解决滑块（成功率>50%）
- ✅ 能够继续采集数据
- ✅ 能够保存到数据库
- ✅ 能够通过Crawlab管理

这个MVP完成后，核心技术方案得到验证，后续可以根据需要扩展更多功能。
## 后续扩展计划
（MVP验证成功后）

### 扩展功能清单
- [ ] 代理IP池集成（当遇到IP风控时）
- [ ] 批量关键词并发处理
- [ ] 更多商品信息提取（价格、图片、销量等）
- [ ] 多电商平台支持
- [ ] 高级反检测技术
- [ ] 实时监控和告警系统
- [ ] 数据分析和可视化界面

### 技术债务
- 当前使用显示模式浏览器便于调试，生产环境可切换为无头模式
- 错误处理机制较简单，后续可增强异常分类和处理策略
- 数据模型较简化，后续可扩展更丰富的字段结构

这样的MVP设计既保证了核心功能的快速验证，又为后续扩展预留了清晰的路径。