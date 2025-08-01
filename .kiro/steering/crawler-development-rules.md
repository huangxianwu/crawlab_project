# 爬虫开发规范 (Crawler Development Rules)

## 代码结构规范

### 项目目录结构
```
crawler-project/
├── main.py              # 主入口文件
├── config.py            # 配置管理
├── models/              # 数据模型
│   ├── __init__.py
│   └── product.py       # 商品数据模型
├── utils/               # 工具类
│   ├── __init__.py
│   ├── webdriver.py     # WebDriver管理
│   ├── database.py      # 数据库操作
│   └── logger.py        # 日志工具
├── handlers/            # 处理器
│   ├── __init__.py
│   ├── slider.py        # 滑块处理
│   └── extractor.py     # 数据提取
├── tests/               # 测试代码目录
│   ├── unit/           # 单元测试
│   ├── integration/    # 集成测试
│   └── demo/           # 演示和验证代码
├── docs/                # 文档目录
│   ├── api/            # API文档
│   ├── deployment/     # 部署文档
│   └── development/    # 开发文档
├── scripts/             # 脚本目录
│   ├── deploy/         # 部署脚本
│   ├── backup/         # 备份脚本
│   └── maintenance/    # 维护脚本
├── temp/                # 临时文件目录
├── backup/              # 备份文件目录
├── requirements.txt     # 依赖包
├── README.md           # 项目说明
└── logs/               # 日志目录
```

### 文件组织规范
**重要原则：所有过程性文件必须归类存放，避免根目录混乱**

1. **测试代码分类存放**
   - `tests/unit/` - 单元测试文件
   - `tests/integration/` - 集成测试文件  
   - `tests/demo/` - 演示和验证代码
   - `tests/mock/` - 模拟测试代码

2. **文档分类存放**
   - `docs/api/` - API接口文档
   - `docs/deployment/` - 部署相关文档
   - `docs/development/` - 开发过程文档
   - `docs/troubleshooting/` - 问题排查文档

3. **脚本分类存放**
   - `scripts/deploy/` - 部署脚本
   - `scripts/backup/` - 备份脚本
   - `scripts/maintenance/` - 维护脚本
   - `scripts/migration/` - 数据迁移脚本

4. **临时和备份文件**
   - `temp/` - 临时文件和中间产物
   - `backup/` - 备份文件和历史版本
   - `archive/` - 归档文件

5. **配置文件分类**
   - `config/` - 各环境配置文件
   - `config/dev/` - 开发环境配置
   - `config/prod/` - 生产环境配置
   - `config/test/` - 测试环境配置

### 代码风格规范
- 使用Python PEP 8编码规范
- 类名使用驼峰命名法：`SliderHandler`
- 函数和变量使用下划线命名法：`extract_product_title`
- 常量使用大写字母：`MAX_RETRY_COUNT = 3`
- 所有函数和类必须有docstring文档

### 文件命名和组织规范
**严格要求：创建任何过程性文件时必须归类存放**

1. **测试文件命名规范**
   ```
   tests/unit/test_slider_handler.py      # 单元测试
   tests/integration/test_full_workflow.py # 集成测试
   tests/demo/demo_webdriver_basic.py     # 基础演示
   tests/demo/verify_crawler_flow.py      # 流程验证
   ```

2. **文档文件命名规范**
   ```
   docs/deployment/crawlab_setup.md       # 部署指南
   docs/development/slider_algorithm.md   # 开发文档
   docs/api/crawler_api_spec.md          # API文档
   docs/troubleshooting/common_issues.md  # 问题排查
   ```

3. **脚本文件命名规范**
   ```
   scripts/deploy/deploy_to_crawlab.py    # 部署脚本
   scripts/backup/backup_database.py     # 备份脚本
   scripts/maintenance/clean_logs.py     # 维护脚本
   ```

4. **开发过程中的文件组织要求**
   - 创建测试代码时，必须放入 `tests/` 对应子目录
   - 编写文档时，必须放入 `docs/` 对应子目录
   - 开发脚本必须放入 `scripts/` 对应子目录
   - 临时文件和实验代码放入 `temp/` 目录
   - 备份文件放入 `backup/` 目录

5. **禁止行为**
   - 禁止在项目根目录创建测试文件（如 `test_*.py`）
   - 禁止在根目录创建临时脚本（如 `temp_*.py`）
   - 禁止在根目录创建备份文件（如 `*.bak`）
   - 禁止在根目录创建演示代码（如 `demo_*.py`）
   - 禁止不经过架构复盘就开始开发新功能
   - 禁止重复实现已有功能而不进行代码复用

### 开发决策流程图
```
开始开发任务
    ↓
检查项目架构 → 了解现有模块 → 确认功能需求
    ↓
现有功能是否满足？
    ↓ 是              ↓ 否
直接使用/扩展    →    是否可扩展现有代码？
    ↓                    ↓ 是        ↓ 否
完成开发        →    扩展现有功能    创建新模块
    ↓                    ↓            ↓
测试验证        ←    测试验证    ←    测试验证
    ↓
文档更新
    ↓
完成
```

## 开发流程规范

### 开发前必要步骤
**强制要求：每次开发任务前必须执行以下步骤**

1. **项目架构复盘**
   ```bash
   # 必须先了解当前项目结构
   tree -I '__pycache__|*.pyc|logs' crawler-project/
   ```
   - 明确各模块的职责和功能
   - 了解现有代码的实现逻辑
   - 识别可复用的组件和工具类

2. **现有功能清单检查**
   - 检查 `utils/` 目录下已有的工具类
   - 检查 `handlers/` 目录下已有的处理器
   - 检查 `models/` 目录下已有的数据模型
   - 检查 `tests/` 目录下已有的测试代码

3. **避免重复开发检查清单**
   - [ ] 所需功能是否已在现有模块中实现？
   - [ ] 是否可以扩展现有类而不是重新创建？
   - [ ] 是否已有类似的测试代码可以参考？
   - [ ] 是否已有相关的配置项可以复用？

4. **文档和规范确认**
   - 阅读 `README.md` 了解项目概况
   - 检查 `docs/` 目录下的相关文档
   - 确认开发规范和代码风格要求

### 开发过程规范
1. **功能开发前**
   - 先检查是否可以扩展现有功能
   - 优先考虑修改现有代码而非创建新文件
   - 新增功能必须符合现有架构设计

2. **代码复用原则**
   - 优先使用现有的工具类和方法
   - 相似功能通过参数化实现，避免代码重复
   - 通用逻辑抽取到 `utils/` 目录

3. **测试代码复用**
   - 检查 `tests/` 目录下是否有类似测试
   - 复用现有的测试工具和模拟数据
   - 扩展现有测试套件而非重新编写

## 爬虫开发最佳实践

### 1. 错误处理规范
```python
def extract_data():
    try:
        # 核心逻辑
        pass
    except TimeoutException:
        logger.error("页面加载超时")
        return None
    except NoSuchElementException:
        logger.error("元素未找到")
        return None
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        return None
```

### 2. 日志记录规范
- 使用统一的日志格式：`[时间] [级别] [模块] 消息`
- 关键操作必须记录日志：搜索、数据提取、滑块处理、数据保存
- 错误日志必须包含详细的错误信息和堆栈跟踪
- 成功操作记录INFO级别，错误记录ERROR级别

### 3. 配置管理规范
```python
# config.py
class Config:
    # 目标网站配置
    TARGET_URL = "https://example.com"
    SEARCH_INPUT_SELECTOR = "#search-input"
    PRODUCT_TITLE_SELECTOR = ".product-title"
    
    # 爬虫行为配置
    MIN_DELAY = 2  # 最小延时(秒)
    MAX_DELAY = 5  # 最大延时(秒)
    MAX_RETRY = 3  # 最大重试次数
    
    # 数据库配置
    MONGO_URI = "mongodb://localhost:27017"
    DATABASE_NAME = "crawler_db"
    COLLECTION_NAME = "products"
```

### 4. 数据模型规范
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ProductData:
    keyword: str
    title: str
    scraped_at: datetime
    slider_encountered: bool = False
    slider_solved: bool = False
    
    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword,
            "title": self.title,
            "scraped_at": self.scraped_at.isoformat(),
            "slider_encountered": self.slider_encountered,
            "slider_solved": self.slider_solved
        }
```

## 滑块处理规范 (基于TikTok项目实战经验)

### 1. 滑块检测标准
```python
def detect_slider(self, page):
    """检测滑块验证码 - 多重检测策略"""
    try:
        # 方法1: 检查HTML中的验证码容器
        html_text = page.html
        if '<div id="captcha_container">' in html_text:
            return True
        
        # 方法2: 检查验证码图片元素
        captcha_imgs = page.eles("tag=img", timeout=5)
        if len(captcha_imgs) >= 2:  # 背景图和滑块图
            return True
        
        # 方法3: 检查滑块拖拽元素
        slider_element = page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=2)
        if slider_element:
            return True
            
        return False
    except Exception as e:
        logger.error(f"滑块检测失败: {e}")
        return False
```

### 2. 滑块处理核心算法 (使用ddddocr)
```python
import ddddocr
import requests
import cv2
import numpy as np

def solve_slider_captcha(self, page):
    """解决滑块验证码 - 基于图像识别"""
    try:
        # 初始化ddddocr滑块检测器
        det = ddddocr.DdddOcr(det=False, ocr=False)
        
        # 获取验证码图片
        imgs = page.eles("tag=img", timeout=10)
        if len(imgs) < 2:
            return False
        
        background_img_url = imgs[0].attr("src")  # 背景图
        target_img_url = imgs[1].attr("src")      # 滑块图
        
        # 下载图片
        background_response = requests.get(background_img_url, timeout=10)
        target_response = requests.get(target_img_url, timeout=10)
        
        if background_response.status_code == 200 and target_response.status_code == 200:
            # 使用ddddocr进行滑块匹配
            background_bytes = background_response.content
            target_bytes = target_response.content
            
            res = det.slide_match(target_bytes, background_bytes)
            if res and "target" in res:
                target_x = res["target"][0]
                
                # 计算实际滑动距离（考虑缩放比例）
                x_offset = imgs[1].rect.location[0] - imgs[0].rect.location[0]
                
                # 获取图片实际尺寸进行缩放计算
                img_array = np.frombuffer(background_bytes, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    height, width = img.shape[:2]
                    actual_x = target_x * (340 / width) - x_offset
                else:
                    actual_x = target_x - x_offset
                
                # 执行滑动操作
                slider_element = page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=5)
                if slider_element:
                    slider_element.drag(actual_x, 10, 0.2)  # 0.2秒完成滑动
                    time.sleep(3)
                    return True
        
        return False
    except Exception as e:
        logger.error(f"滑块处理失败: {e}")
        return False
```

### 3. 滑块处理完整流程
```python
def handle_captcha_with_retry(self, page=None):
    """带重试机制的滑块处理"""
    if page is None:
        page = self.page
    
    # 最多重试3次
    for attempt in range(3):
        try:
            # 检测是否有滑块
            if not self.detect_slider(page):
                return False  # 没有滑块，继续正常流程
            
            logger.info(f"检测到滑块验证，开始处理 (尝试 {attempt + 1}/3)")
            
            # 尝试解决滑块
            if self.solve_slider_captcha(page):
                # 验证是否成功
                time.sleep(2)
                if not self.detect_slider(page):
                    logger.info("滑块验证成功")
                    return False  # 成功解决
            
            # 失败后刷新页面重试
            if attempt < 2:
                logger.warning(f"滑块处理失败，刷新页面重试")
                page.refresh(ignore_cache=True)
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"滑块处理异常: {e}")
            continue
    
    logger.error("滑块处理失败，已尝试3次")
    return True  # 返回True表示有滑块且无法解决
```

### 4. 备用方案 - 随机滑动
```python
def fallback_random_slide(self, page):
    """备用方案：随机滑动距离"""
    try:
        import random
        slide_distance = random.randint(100, 200)
        
        slider_element = page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=5)
        if slider_element:
            # 生成人工轨迹
            trajectory = self.generate_human_trajectory(slide_distance)
            
            for step in trajectory:
                slider_element.drag(step, 0, 0.05)  # 分步滑动
                time.sleep(0.02)
            
            return True
    except Exception as e:
        logger.error(f"随机滑动失败: {e}")
        return False
```

### 5. 人工轨迹生成算法
```python
def generate_human_trajectory(self, distance):
    """生成模拟人工的滑动轨迹"""
    import random
    
    trajectory = []
    current = 0
    mid = distance * 0.8  # 80%处开始减速
    
    while current < distance:
        if current < mid:
            # 加速阶段：随机加速度
            a = random.uniform(1, 3)
        else:
            # 减速阶段：随机减速度
            a = random.uniform(-3, -1)
        
        # 计算移动步长
        v0 = random.uniform(0, 1)
        move = v0 + 0.5 * a
        current += move
        
        if current > distance:
            move = distance - (current - move)
        
        trajectory.append(round(move))
    
    return trajectory
```

### 6. 依赖包要求
```python
# requirements.txt 必须包含
ddddocr>=1.4.7          # 滑块识别核心库
opencv-python>=4.5.0    # 图像处理
numpy>=1.21.0           # 数值计算
requests>=2.25.0        # HTTP请求
DrissionPage>=3.0.0     # 浏览器自动化 (可选，也可用selenium)
```

### 7. 滑块处理最佳实践
- **多重检测**: 使用HTML检查、元素检查、图片检查等多种方式
- **智能识别**: 优先使用ddddocr进行精确位置识别
- **备用方案**: 识别失败时使用随机滑动作为备选
- **重试机制**: 最多重试3次，每次重试前刷新页面
- **轨迹模拟**: 生成加速-减速的人工轨迹
- **异常处理**: 完善的异常捕获和日志记录

## 数据库操作规范

### 1. 连接管理
- 使用连接池管理数据库连接
- 操作完成后及时关闭连接
- 连接异常时有重连机制

### 2. 数据插入规范
- 批量插入优于单条插入
- 插入前进行数据验证
- 插入失败时记录详细错误信息
- 支持数据去重机制

### 3. 查询优化
- 为常用查询字段创建索引
- 避免全表扫描查询
- 查询结果限制合理的数量

## 性能优化规范

### 1. 内存管理
- 及时释放不用的WebDriver实例
- 避免内存泄漏，定期清理缓存
- 大量数据处理时使用生成器

### 2. 并发控制
- 合理设置并发数量，避免过载
- 使用信号量控制资源访问
- 避免竞态条件

### 3. 网络优化
- 设置合理的请求超时时间
- 使用Keep-Alive连接复用
- 实现智能重试机制

## 测试规范

### 1. 单元测试
- 每个核心函数都要有单元测试
- 测试覆盖率不低于80%
- 测试用例包含正常和异常情况

### 2. 集成测试
- 测试完整的爬取流程
- 测试滑块处理的成功率
- 测试数据存储的完整性

### 3. 性能测试
- 测试单个任务的处理时间
- 测试系统的并发处理能力
- 监控内存和CPU使用情况

## Git提交规范

### 1. 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 2. 提交类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 3. 提交示例
```
feat(slider): 实现滑块验证自动处理功能

- 添加滑块检测算法
- 实现人工轨迹生成
- 集成滑块处理到主流程

Closes #123
```

## 安全规范

### 1. 敏感信息保护
- 不在代码中硬编码密码、API密钥
- 使用环境变量或配置文件管理敏感信息
- Git提交前检查是否包含敏感信息

### 2. 反爬虫对抗
- 遵守robots.txt协议
- 控制请求频率，避免对目标网站造成压力
- 使用合理的User-Agent标识

### 3. 数据安全
- 采集的数据仅用于合法目的
- 不采集用户隐私信息
- 数据存储加密保护

## 代码复用和重构规范

### 1. 代码复用检查
**每次开发前必须执行的检查**
```python
# 检查现有工具类
ls -la utils/
# 检查现有处理器
ls -la handlers/
# 检查现有模型
ls -la models/
# 检查现有测试
find tests/ -name "*.py" -type f
```

### 2. 功能扩展优先级
1. **优先级1**: 扩展现有类的方法
2. **优先级2**: 继承现有类创建子类
3. **优先级3**: 创建新的工具类
4. **优先级4**: 创建全新模块

### 3. 重构指导原则
- 发现重复代码时立即重构
- 超过3次相似实现必须抽取公共方法
- 新功能开发完成后检查是否需要重构现有代码

## 监控和维护规范

### 1. 日志监控
- 定期检查错误日志
- 监控爬虫成功率
- 设置关键指标告警

### 2. 性能监控
- 监控系统资源使用情况
- 跟踪爬取效率变化
- 定期优化性能瓶颈

### 3. 维护更新
- 定期更新依赖包版本
- 适配目标网站的变化
- 优化爬虫策略和算法

### 4. 代码维护
- 定期检查代码重复度
- 及时重构过时的实现
- 保持项目架构的清晰性
## 滑
块处理完整示例代码

### handlers/slider.py 模板
```python
"""
滑块验证处理器
基于TikTok项目实战经验，使用ddddocr进行智能识别
"""
import time
import random
import requests
import cv2
import numpy as np
import ddddocr
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from utils.logger import logger


class SliderHandler:
    """滑块验证处理器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        # 初始化ddddocr
        try:
            self.det = ddddocr.DdddOcr(det=False, ocr=False)
            logger.info("ddddocr滑块检测器初始化成功")
        except Exception as e:
            logger.error(f"ddddocr初始化失败: {e}")
            self.det = None
    
    def detect_slider(self):
        """检测是否存在滑块验证"""
        try:
            # 方法1: 检查常见的滑块容器
            slider_selectors = [
                "#captcha_container",
                ".captcha-container", 
                ".slider-container",
                ".slide-verify",
                "[class*='captcha']",
                "[id*='captcha']"
            ]
            
            for selector in slider_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        logger.info(f"检测到滑块容器: {selector}")
                        return True
                except:
                    continue
            
            # 方法2: 检查滑块图片
            try:
                imgs = self.driver.find_elements(By.TAG_NAME, "img")
                captcha_imgs = [img for img in imgs if 
                              'captcha' in img.get_attribute('src') or 
                              'verify' in img.get_attribute('src')]
                if len(captcha_imgs) >= 2:
                    logger.info("检测到滑块验证图片")
                    return True
            except:
                pass
            
            # 方法3: 检查页面源码
            page_source = self.driver.page_source
            captcha_keywords = ['captcha', 'slider', 'verify', '滑块', '验证']
            if any(keyword in page_source.lower() for keyword in captcha_keywords):
                logger.info("页面源码中检测到验证码相关内容")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"滑块检测失败: {e}")
            return False
    
    def solve_slider_captcha(self):
        """解决滑块验证码"""
        if not self.det:
            logger.warning("ddddocr未初始化，使用备用方案")
            return self.fallback_random_slide()
        
        try:
            # 查找滑块图片
            imgs = self.driver.find_elements(By.TAG_NAME, "img")
            if len(imgs) < 2:
                logger.warning("滑块图片不足，使用备用方案")
                return self.fallback_random_slide()
            
            # 获取背景图和滑块图
            background_img = imgs[0]
            target_img = imgs[1]
            
            background_url = background_img.get_attribute("src")
            target_url = target_img.get_attribute("src")
            
            if not background_url or not target_url:
                logger.warning("无法获取滑块图片URL")
                return self.fallback_random_slide()
            
            # 下载图片
            background_response = requests.get(background_url, timeout=10)
            target_response = requests.get(target_url, timeout=10)
            
            if background_response.status_code != 200 or target_response.status_code != 200:
                logger.warning("滑块图片下载失败")
                return self.fallback_random_slide()
            
            # 使用ddddocr识别滑块位置
            background_bytes = background_response.content
            target_bytes = target_response.content
            
            res = self.det.slide_match(target_bytes, background_bytes)
            if not res or "target" not in res:
                logger.warning("ddddocr识别失败，使用备用方案")
                return self.fallback_random_slide()
            
            target_x = res["target"][0]
            logger.info(f"ddddocr识别到滑块位置: {target_x}")
            
            # 计算实际滑动距离
            actual_distance = self.calculate_actual_distance(
                target_x, background_img, target_img, background_bytes
            )
            
            # 执行滑动
            return self.perform_slide(actual_distance)
            
        except Exception as e:
            logger.error(f"滑块识别处理失败: {e}")
            return self.fallback_random_slide()
    
    def calculate_actual_distance(self, target_x, bg_img, target_img, bg_bytes):
        """计算实际滑动距离"""
        try:
            # 获取图片在页面中的位置
            bg_location = bg_img.location
            target_location = target_img.location
            x_offset = target_location['x'] - bg_location['x']
            
            # 获取图片实际尺寸
            img_array = np.frombuffer(bg_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is not None:
                height, width = img.shape[:2]
                # 获取页面中图片的显示尺寸
                bg_size = bg_img.size
                scale_ratio = bg_size['width'] / width
                actual_distance = target_x * scale_ratio - x_offset
            else:
                actual_distance = target_x - x_offset
            
            logger.info(f"计算实际滑动距离: {actual_distance}")
            return max(0, actual_distance)
            
        except Exception as e:
            logger.error(f"距离计算失败: {e}")
            return target_x
    
    def perform_slide(self, distance):
        """执行滑动操作"""
        try:
            # 查找滑块元素
            slider_selectors = [
                ".slider-button",
                ".slide-btn", 
                "[class*='slider']",
                "[class*='drag']"
            ]
            
            slider_element = None
            for selector in slider_selectors:
                try:
                    slider_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if slider_element.is_displayed():
                        break
                except:
                    continue
            
            if not slider_element:
                logger.error("未找到滑块元素")
                return False
            
            # 生成人工轨迹
            trajectory = self.generate_human_trajectory(distance)
            
            # 执行滑动
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_element)
            
            for step in trajectory:
                actions.move_by_offset(step, 0)
                time.sleep(random.uniform(0.01, 0.03))
            
            actions.release()
            actions.perform()
            
            logger.info("滑动操作执行完成")
            time.sleep(2)
            
            # 验证是否成功
            return not self.detect_slider()
            
        except Exception as e:
            logger.error(f"滑动操作失败: {e}")
            return False
    
    def generate_human_trajectory(self, distance):
        """生成模拟人工的滑动轨迹"""
        trajectory = []
        current = 0
        mid = distance * 0.8  # 80%处开始减速
        
        while current < distance:
            if current < mid:
                # 加速阶段
                a = random.uniform(1, 3)
            else:
                # 减速阶段
                a = random.uniform(-3, -1)
            
            v0 = random.uniform(0, 1)
            move = v0 + 0.5 * a
            current += move
            
            if current > distance:
                move = distance - (current - move)
            
            if move > 0:
                trajectory.append(round(move))
        
        logger.debug(f"生成轨迹: {trajectory}")
        return trajectory
    
    def fallback_random_slide(self):
        """备用方案：随机滑动"""
        try:
            logger.info("使用随机滑动备用方案")
            distance = random.randint(100, 200)
            return self.perform_slide(distance)
        except Exception as e:
            logger.error(f"随机滑动失败: {e}")
            return False
    
    def handle_captcha_with_retry(self, max_retries=3):
        """带重试机制的滑块处理"""
        for attempt in range(max_retries):
            try:
                # 检测滑块
                if not self.detect_slider():
                    logger.info("未检测到滑块验证")
                    return False
                
                logger.info(f"检测到滑块验证，开始处理 (尝试 {attempt + 1}/{max_retries})")
                
                # 尝试解决滑块
                if self.solve_slider_captcha():
                    logger.info("滑块验证成功")
                    return False
                
                # 失败后等待并重试
                if attempt < max_retries - 1:
                    wait_time = random.uniform(2, 5)
                    logger.warning(f"滑块处理失败，等待 {wait_time:.1f}s 后重试")
                    time.sleep(wait_time)
                    
                    # 刷新页面
                    self.driver.refresh()
                    time.sleep(3)
                
            except Exception as e:
                logger.error(f"滑块处理异常: {e}")
                continue
        
        logger.error(f"滑块处理失败，已尝试 {max_retries} 次")
        return True  # 返回True表示有滑块且无法解决
```

### 使用示例
```python
from handlers.slider import SliderHandler

# 在爬虫主流程中使用
def crawl_with_slider_handling(driver, url):
    driver.get(url)
    
    # 初始化滑块处理器
    slider_handler = SliderHandler(driver)
    
    # 处理滑块验证
    has_unsolved_captcha = slider_handler.handle_captcha_with_retry()
    
    if has_unsolved_captcha:
        logger.error("滑块验证无法解决，跳过当前任务")
        return None
    
    # 继续正常的爬取流程
    # ... 其他爬取逻辑
```

这个实现基于TikTok项目的实战经验，提供了完整的滑块处理解决方案。