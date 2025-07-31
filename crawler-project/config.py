"""
爬虫配置管理
集中管理所有配置参数
"""
import os
from typing import List


class Config:
    """爬虫配置类"""
    
    # ==================== 目标网站配置 ====================
    
    # 目标电商网站URL（基于TikTok Shop）
    TARGET_URL = "https://www.tiktok.com/shop/search"
    BASE_URL = "https://www.tiktok.com"
    
    # API接口配置（参考TikTok项目）
    API_URLS = {
        "product_list": "https://www.tiktok.com/api/shop/brandy_desktop/s/product_list",
        "store_products": "https://www.tiktok.com/api/shop/brandy_desktop/store/product_list",
        "product_detail": "https://www.tiktok.com/api/shop/brandy_desktop/product/detail"
    }
    
    # 搜索相关选择器（基于TikTok Shop页面结构）
    SEARCH_INPUT_SELECTOR = "input[placeholder*='Search']"  # 搜索输入框
    SEARCH_BUTTON_SELECTOR = "button[type='submit']"  # 搜索按钮
    
    # 商品信息选择器（基于TikTok Shop商品卡片结构）
    PRODUCT_CARD_SELECTOR = "[data-e2e='search-product-item']"  # 商品卡片
    PRODUCT_TITLE_SELECTOR = "[data-e2e='product-title']"  # 商品标题
    PRODUCT_PRICE_SELECTOR = "[data-e2e='product-price']"  # 商品价格
    PRODUCT_LINK_SELECTOR = "a[href*='/product/']"  # 商品链接
    PRODUCT_IMAGE_SELECTOR = "img[alt*='product']"  # 商品图片
    PRODUCT_SHOP_SELECTOR = "[data-e2e='shop-name']"  # 店铺名称
    PRODUCT_RATING_SELECTOR = "[data-e2e='product-rating']"  # 商品评分
    PRODUCT_SALES_SELECTOR = "[data-e2e='product-sales']"  # 销量信息
    
    # 分页相关选择器
    NEXT_PAGE_SELECTOR = "[data-e2e='search-pagination-next']"  # 下一页按钮
    PAGE_INFO_SELECTOR = "[data-e2e='pagination-info']"  # 页面信息
    LOAD_MORE_SELECTOR = "[data-e2e='load-more-button']"  # 加载更多按钮
    
    # 滑块验证相关选择器（基于TikTok验证码）
    CAPTCHA_CONTAINER_SELECTOR = "#captcha_container"  # 验证码容器
    SLIDER_TRACK_SELECTOR = ".secsdk-captcha-drag-wrapper"  # 滑块轨道
    SLIDER_BUTTON_SELECTOR = ".secsdk-captcha-drag-icon"  # 滑块按钮
    CAPTCHA_IMAGE_SELECTOR = ".captcha-verify-image"  # 验证码图片
    
    # ==================== 爬虫行为配置 ====================
    
    # 请求延时配置（秒）
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
    
    # ==================== 浏览器配置 ====================
    
    # Chrome浏览器配置
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",  # 禁用图片加载以提高速度
        "--disable-javascript",  # 根据需要启用/禁用JS
    ]
    
    # User-Agent池
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]
    
    # 窗口大小配置
    WINDOW_SIZES = [
        (1920, 1080),
        (1366, 768),
        (1440, 900),
        (1536, 864),
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
    
    # ==================== 关键词配置 ====================
    
    # 默认测试关键词
    DEFAULT_KEYWORDS = [
        "手机壳",
        "数据线",
        "充电器",
        "耳机",
        "手机支架"
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
    
    # ==================== 代理配置 ====================
    
    # 代理配置（暂时不启用）
    USE_PROXY = False
    PROXY_LIST = []
    PROXY_TIMEOUT = 10
    
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
            
            return True
            
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False
    
    @classmethod
    def print_config(cls):
        """打印当前配置信息"""
        print("当前配置信息:")
        print(f"  目标网站: {cls.TARGET_URL}")
        print(f"  数据库: {cls.MONGO_URI}")
        print(f"  延时范围: {cls.MIN_DELAY}-{cls.MAX_DELAY}秒")
        print(f"  最大重试: {cls.MAX_RETRY}次")
        print(f"  调试模式: {cls.DEBUG_MODE}")
        print(f"  无头模式: {cls.HEADLESS_MODE}")
        print(f"  关键词数量: {len(cls.get_keywords())}个")