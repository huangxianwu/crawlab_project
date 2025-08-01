"""
爬虫配置管理
基于TikTok项目实战经验的完整配置
参考: https://github.com/huangxianwu/tiktok_web_crawler_pyqt
"""
import os
from typing import List


class Config:
    """爬虫配置类 - 基于TikTok项目实战经验"""
    
    # ==================== 目标网站配置 ====================
    
    # TikTok Shop URL配置（重要：确保URL正确）
    BASE_URL = "https://www.tiktok.com"
    TARGET_URL = "https://www.tiktok.com/shop"
    SHOP_BASE_URL = "https://www.tiktok.com/shop"
    SEARCH_BASE_URL = "https://www.tiktok.com/shop/s"  # 搜索基础URL
    
    # 搜索URL构建方法
    @classmethod
    def build_search_url(cls, keyword: str) -> str:
        """
        构建TikTok Shop搜索URL
        格式: https://www.tiktok.com/shop/s/{encoded_keyword}
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            str: 完整的搜索URL
        """
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword)
        return f"{cls.SEARCH_BASE_URL}/{encoded_keyword}"
    
    # ==================== 页面选择器配置 ====================
    
    # 搜索相关选择器
    SEARCH_INPUT_SELECTOR = "input[placeholder*='Search']"  # 搜索输入框
    SEARCH_BUTTON_SELECTOR = "button[type='submit']"  # 搜索按钮
    SEARCH_RESULTS_SELECTOR = "[data-e2e='search-result']"  # 搜索结果容器
    
    # 商品相关选择器（基于TikTok Shop实际页面结构）
    PRODUCT_LIST_SELECTOR = "[data-e2e='search-product-list']"  # 商品列表容器
    PRODUCT_CARD_SELECTOR = "[data-e2e='search-product-item']"  # 商品卡片
    PRODUCT_TITLE_SELECTOR = "[data-e2e='product-title']"  # 商品标题
    PRODUCT_PRICE_SELECTOR = "[data-e2e='product-price']"  # 商品价格
    PRODUCT_IMAGE_SELECTOR = "[data-e2e='product-image']"  # 商品图片
    PRODUCT_LINK_SELECTOR = "a[data-e2e='product-link']"  # 商品链接
    SHOP_NAME_SELECTOR = "[data-e2e='shop-name']"  # 店铺名称
    
    # 备用选择器（当data-e2e属性不可用时）
    PRODUCT_CARD_BACKUP = ".product-card, .item-card, [class*='product']"
    PRODUCT_TITLE_BACKUP = ".product-title, .item-title, h3, h4, [class*='title']"
    PRODUCT_PRICE_BACKUP = ".price, .product-price, [class*='price']"
    PRODUCT_IMAGE_BACKUP = "img[alt*='product'], img[class*='product']"
    
    # ==================== 滑块验证配置 ====================
    
    # 滑块检测选择器（基于TikTok实际验证码结构）
    CAPTCHA_CONTAINER_SELECTOR = "#captcha_container"  # 验证码容器
    CAPTCHA_WRAPPER_SELECTOR = ".secsdk-captcha-drag-wrapper"  # 滑块包装器
    CAPTCHA_VISIBLE_SELECTOR = "[style*='display: block']"  # 可见的验证码
    
    # 滑块操作选择器
    SLIDER_TRACK_SELECTOR = ".secsdk-captcha-drag-wrapper"  # 滑块轨道
    SLIDER_BUTTON_SELECTOR = ".secsdk-captcha-drag-icon"  # 滑块按钮
    SLIDER_DRAG_ELEMENT_XPATH = "//*[@id='secsdk-captcha-drag-wrapper']/div[2]"  # 拖拽元素
    
    # 验证码图片选择器
    CAPTCHA_IMAGE_SELECTOR = ".captcha-verify-image"  # 验证码图片
    BACKGROUND_IMAGE_SELECTOR = ".captcha-verify-image:first-child"  # 背景图
    SLIDER_IMAGE_SELECTOR = ".captcha-verify-image:last-child"  # 滑块图
    
    # ==================== 爬虫行为配置 ====================
    
    # 延时配置（秒）
    MIN_DELAY = 2  # 最小延时
    MAX_DELAY = 5  # 最大延时
    PAGE_LOAD_TIMEOUT = 30  # 页面加载超时
    ELEMENT_WAIT_TIMEOUT = 10  # 元素等待超时
    
    # 重试配置
    MAX_RETRY = 3  # 最大重试次数
    RETRY_DELAY = 5  # 重试间隔（秒）
    
    # 滑块处理配置
    SLIDER_MAX_RETRY = 3  # 滑块最大重试次数
    SLIDER_TIMEOUT = 30  # 滑块处理超时时间
    SLIDE_DURATION = 0.2  # 滑动持续时间（秒）
    
    # ==================== 浏览器配置 ====================
    
    # Chrome浏览器选项
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
    ]
    
    # User-Agent池（模拟真实浏览器）
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    # 窗口大小配置
    WINDOW_SIZES = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
    ]
    
    # ==================== 数据库配置 ====================
    
    # MongoDB配置
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "crawler_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "products")
    
    # 数据库连接配置
    MONGO_CONNECT_TIMEOUT = 5000  # 连接超时（毫秒）
    MONGO_SERVER_SELECTION_TIMEOUT = 5000  # 服务器选择超时（毫秒）
    
    # ==================== 日志配置 ====================
    
    # 日志级别
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # 日志文件配置
    LOG_DIR = "logs"
    LOG_FILE = "crawler.log"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5  # 保留5个备份文件
    
    # 日志格式
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # ==================== 测试关键词配置 ====================
    
    # 默认测试关键词
    DEFAULT_KEYWORDS = [
        "cute clothes",
        "phone case", 
        "wireless charger",
        "bluetooth headphones",
        "laptop stand"
    ]
    
    # 关键词文件路径
    KEYWORDS_FILE = "keywords.txt"
    
    # ==================== 输出配置 ====================
    
    # 输出目录
    OUTPUT_DIR = "output"
    
    # 输出文件格式
    OUTPUT_FORMATS = ["json", "csv"]
    
    # 每批次处理的关键词数量
    BATCH_SIZE = 10
    
    # 每个关键词最大采集页数
    MAX_PAGES_PER_KEYWORD = 3
    
    # 每页最大采集商品数
    MAX_PRODUCTS_PER_PAGE = 50
    
    # ==================== 调试配置 ====================
    
    # 调试模式
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # 显示浏览器界面（调试用）
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    
    # 截图保存
    SAVE_SCREENSHOTS = DEBUG_MODE
    SCREENSHOT_DIR = "screenshots"
    
    # ==================== 性能配置 ====================
    
    # 并发配置
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "1"))  # MVP版本使用单线程
    
    # 内存限制
    MAX_MEMORY_MB = 1024  # 最大内存使用量（MB）
    
    @classmethod
    def get_keywords(cls) -> List[str]:
        """
        获取关键词列表
        优先从文件读取，如果文件不存在则使用默认关键词
        """
        try:
            if os.path.exists(cls.KEYWORDS_FILE):
                with open(cls.KEYWORDS_FILE, 'r', encoding='utf-8') as f:
                    keywords = [line.strip() for line in f if line.strip()]
                    return keywords if keywords else cls.DEFAULT_KEYWORDS
            else:
                return cls.DEFAULT_KEYWORDS
        except Exception:
            return cls.DEFAULT_KEYWORDS
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        验证配置的有效性
        """
        try:
            # 检查必要的目录
            os.makedirs(cls.LOG_DIR, exist_ok=True)
            os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
            
            if cls.SAVE_SCREENSHOTS:
                os.makedirs(cls.SCREENSHOT_DIR, exist_ok=True)
            
            # 检查配置参数
            assert cls.MIN_DELAY > 0, "MIN_DELAY必须大于0"
            assert cls.MAX_DELAY >= cls.MIN_DELAY, "MAX_DELAY必须大于等于MIN_DELAY"
            assert cls.MAX_RETRY > 0, "MAX_RETRY必须大于0"
            assert cls.PAGE_LOAD_TIMEOUT > 0, "PAGE_LOAD_TIMEOUT必须大于0"
            
            # 验证URL格式
            assert cls.BASE_URL.startswith("https://"), "BASE_URL必须是HTTPS"
            assert cls.SEARCH_BASE_URL.startswith("https://"), "SEARCH_BASE_URL必须是HTTPS"
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False
    
    @classmethod
    def print_config(cls):
        """打印当前配置信息"""
        print("TikTok爬虫配置信息:")
        print(f"  基础URL: {cls.BASE_URL}")
        print(f"  搜索URL: {cls.SEARCH_BASE_URL}")
        print(f"  数据库: {cls.MONGO_URI}")
        print(f"  延时范围: {cls.MIN_DELAY}-{cls.MAX_DELAY}秒")
        print(f"  最大重试: {cls.MAX_RETRY}次")
        print(f"  滑块重试: {cls.SLIDER_MAX_RETRY}次")
        print(f"  调试模式: {cls.DEBUG_MODE}")
        print(f"  无头模式: {cls.HEADLESS_MODE}")
        print(f"  关键词数量: {len(cls.get_keywords())}个")
        
        # 测试URL构建
        test_keyword = "cute clothes"
        test_url = cls.build_search_url(test_keyword)
        print(f"  测试URL: {test_url}")