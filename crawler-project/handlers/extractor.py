"""
数据提取器
基于TikTok项目经验，提供商品数据提取功能
"""
import os
import sys
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

# 🔧 关键修复：多重路径修复策略
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 多重路径修复策略
paths_to_add = [
    project_root,              # 项目根目录
    current_dir,               # 当前目录
    os.getcwd(),               # 工作目录
    '.',                       # 相对当前目录
]

# 将所有可能的路径都添加到sys.path的最前面
for path in reversed(paths_to_add):
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)

# 🔍 增强调试信息 - 始终显示以便Crawlab调试
print("🔍 [DEBUG] handlers/extractor.py 路径调试信息")
print(f"[DEBUG] 当前文件: {__file__}")
print(f"[DEBUG] current_dir: {current_dir}")
print(f"[DEBUG] project_root: {project_root}")
print(f"[DEBUG] 工作目录: {os.getcwd()}")
print(f"[DEBUG] sys.path前5个:")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

# 检查关键文件是否存在
key_files = ['utils/__init__.py', 'utils/logger.py', 'config.py', 'models/__init__.py']
for file_path in key_files:
    full_path = os.path.join(project_root, file_path)
    exists = os.path.exists(full_path)
    print(f"[DEBUG] {file_path}: 存在={exists} ({full_path})")

# 尝试直接导入测试
print(f"[DEBUG] handlers/extractor.py 导入测试:")
try:
    import utils
    print(f"  ✅ import utils 成功")
except Exception as e:
    print(f"  ❌ import utils 失败: {e}")

try:
    from utils.logger import get_logger
    print(f"  ✅ from utils.logger import get_logger 成功")
except Exception as e:
    print(f"  ❌ from utils.logger import get_logger 失败: {e}")

try:
    import config
    print(f"  ✅ import config 成功")
except Exception as e:
    print(f"  ❌ import config 失败: {e}")

try:
    from models.product import ProductData
    print(f"  ✅ from models.product import ProductData 成功")
except Exception as e:
    print(f"  ❌ from models.product import ProductData 失败: {e}")

print("-" * 40)

# 强制刷新模块缓存（防止缓存问题）
modules_to_clear = ['utils', 'config', 'models']
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

from models.product import ProductData
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class DataExtractor:
    """数据提取器 - 基于TikTok项目经验"""
    
    def __init__(self, webdriver_manager):
        """
        初始化数据提取器
        
        Args:
            webdriver_manager: WebDriver管理器实例
        """
        self.webdriver_manager = webdriver_manager
        self.extracted_products = []
        
        logger.info("数据提取器初始化完成")
    
    def extract_products_by_keyword(self, keyword: str, max_pages: int = 1) -> List[ProductData]:
        """
        根据关键词提取商品数据
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大提取页数
            
        Returns:
            List[ProductData]: 提取的商品数据列表
        """
        products = []
        
        try:
            logger.info(f"开始提取关键词 '{keyword}' 的商品数据，最大页数: {max_pages}")
            
            # 执行搜索
            if not self.webdriver_manager.search_products(keyword):
                logger.error(f"搜索关键词 '{keyword}' 失败")
                return products
            
            # 逐页提取数据
            for page_num in range(1, max_pages + 1):
                logger.info(f"提取第 {page_num} 页数据")
                
                # 从当前页面提取商品
                page_products_data = self.webdriver_manager.extract_products_from_page(keyword, page_num)
                
                # 转换为ProductData对象
                for product_data in page_products_data:
                    try:
                        product = self.create_product_from_data(product_data)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logger.warning(f"创建商品对象失败: {e}")
                        continue
                
                # 如果不是最后一页，尝试翻页
                if page_num < max_pages:
                    if not self.navigate_to_next_page():
                        logger.warning(f"无法翻到第 {page_num + 1} 页，停止提取")
                        break
                
                # 随机延时
                time.sleep(random.uniform(2, 4))
            
            logger.info(f"关键词 '{keyword}' 提取完成，共获得 {len(products)} 个商品")
            self.extracted_products.extend(products)
            
            return products
            
        except Exception as e:
            logger.error(f"提取关键词 '{keyword}' 的商品数据失败: {e}")
            return products
    
    def create_product_from_data(self, product_data: Dict[str, Any]) -> Optional[ProductData]:
        """
        从原始数据创建ProductData对象
        
        Args:
            product_data: 原始商品数据
            
        Returns:
            ProductData: 商品数据对象，创建失败返回None
        """
        try:
            # 验证必要字段
            if not product_data.get('title'):
                logger.warning("商品标题为空，跳过")
                return None
            
            # 创建ProductData对象
            product = ProductData(
                keyword=product_data.get('keyword', ''),
                title=product_data.get('title', ''),
                scraped_at=datetime.now(),
                slider_encountered=product_data.get('slider_encountered', False),
                slider_solved=product_data.get('slider_solved', False)
            )
            
            return product
            
        except Exception as e:
            logger.error(f"创建ProductData对象失败: {e}")
            return None
    
    def navigate_to_next_page(self) -> bool:
        """
        导航到下一页
        
        Returns:
            bool: 是否成功翻页
        """
        try:
            driver = self.webdriver_manager.get_driver()
            
            # 尝试查找下一页按钮
            next_page_selectors = [
                Config.NEXT_PAGE_SELECTOR,
                ".next-page",
                "[aria-label*='next']",
                "[class*='next']",
                "button:contains('下一页')",
                "a:contains('Next')"
            ]
            
            for selector in next_page_selectors:
                try:
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    
                    wait = WebDriverWait(driver, 5)
                    next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    if next_button.is_enabled():
                        next_button.click()
                        logger.info("成功点击下一页按钮")
                        
                        # 等待页面加载
                        time.sleep(random.uniform(3, 5))
                        return True
                        
                except Exception:
                    continue
            
            # 尝试滚动加载更多
            logger.info("未找到下一页按钮，尝试滚动加载")
            self.webdriver_manager.scroll_page(3)
            
            return False
            
        except Exception as e:
            logger.error(f"翻页失败: {e}")
            return False
    
    def apply_filters(self, products: List[ProductData], filters: Dict[str, Any]) -> List[ProductData]:
        """
        应用筛选条件
        
        Args:
            products: 商品列表
            filters: 筛选条件
            
        Returns:
            List[ProductData]: 筛选后的商品列表
        """
        filtered_products = []
        
        try:
            min_price = filters.get('min_price', 0)
            max_price = filters.get('max_price', float('inf'))
            min_sales = filters.get('min_sales', 0)
            max_sales = filters.get('max_sales', float('inf'))
            
            for product in products:
                # 由于简化版本只有标题，这里主要做标题筛选
                title = product.title.lower()
                
                # 标题关键词筛选
                exclude_keywords = filters.get('exclude_keywords', [])
                if any(keyword.lower() in title for keyword in exclude_keywords):
                    continue
                
                include_keywords = filters.get('include_keywords', [])
                if include_keywords and not any(keyword.lower() in title for keyword in include_keywords):
                    continue
                
                filtered_products.append(product)
            
            logger.info(f"筛选完成: {len(products)} -> {len(filtered_products)}")
            return filtered_products
            
        except Exception as e:
            logger.error(f"应用筛选条件失败: {e}")
            return products
    
    def extract_product_details(self, product_url: str) -> Dict[str, Any]:
        """
        提取商品详细信息
        
        Args:
            product_url: 商品详情页URL
            
        Returns:
            Dict: 商品详细信息
        """
        details = {}
        
        try:
            # 导航到商品详情页
            if not self.webdriver_manager.navigate_to_url(product_url):
                return details
            
            driver = self.webdriver_manager.get_driver()
            
            # 提取详细信息（根据实际页面结构调整）
            detail_selectors = {
                'description': '.product-description',
                'specifications': '.product-specs',
                'reviews_count': '.reviews-count',
                'seller_info': '.seller-info'
            }
            
            for key, selector in detail_selectors.items():
                try:
                    from selenium.webdriver.common.by import By
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    details[key] = element.text.strip()
                except Exception:
                    details[key] = ''
            
            logger.debug(f"提取商品详情完成: {product_url}")
            
        except Exception as e:
            logger.error(f"提取商品详情失败: {e}")
        
        return details
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """
        获取提取统计信息
        
        Returns:
            Dict: 统计信息
        """
        stats = {
            'total_products': len(self.extracted_products),
            'keywords_processed': len(set(p.keyword for p in self.extracted_products)),
            'slider_encountered_count': sum(1 for p in self.extracted_products if p.slider_encountered),
            'slider_solved_count': sum(1 for p in self.extracted_products if p.slider_solved),
            'extraction_time': time.time()
        }
        
        if stats['slider_encountered_count'] > 0:
            stats['slider_success_rate'] = (stats['slider_solved_count'] / stats['slider_encountered_count']) * 100
        else:
            stats['slider_success_rate'] = 0
        
        return stats
    
    def clear_extracted_data(self):
        """清空已提取的数据"""
        self.extracted_products.clear()
        logger.info("已清空提取的数据")
    
    def export_to_dict(self) -> List[Dict[str, Any]]:
        """
        导出数据为字典列表
        
        Returns:
            List[Dict]: 商品数据字典列表
        """
        return [product.to_dict() for product in self.extracted_products]
    
    def validate_product_data(self, product_data: Dict[str, Any]) -> bool:
        """
        验证商品数据的有效性
        
        Args:
            product_data: 商品数据
            
        Returns:
            bool: 数据是否有效
        """
        try:
            # 检查必要字段
            required_fields = ['title', 'keyword']
            for field in required_fields:
                if not product_data.get(field):
                    logger.warning(f"商品数据缺少必要字段: {field}")
                    return False
            
            # 检查标题长度
            title = product_data.get('title', '')
            if len(title) < 5 or len(title) > 200:
                logger.warning(f"商品标题长度异常: {len(title)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证商品数据失败: {e}")
            return False