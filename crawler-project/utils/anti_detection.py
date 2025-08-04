"""
反检测措施工具
包含随机延时、User-Agent设置、请求间隔控制等功能
"""
import time
import random
import logging
from typing import Optional, List
from utils.logger import get_logger

logger = get_logger(__name__)

class AntiDetectionManager:
    """反检测措施管理器"""
    
    # 真实的User-Agent列表
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """
        初始化反检测管理器
        
        Args:
            min_delay: 最小延时（秒）
            max_delay: 最大延时（秒）
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.request_count = 0
        
        logger.info(f"反检测管理器初始化 - 延时范围: {min_delay}-{max_delay}秒")
    
    def get_random_user_agent(self) -> str:
        """
        获取随机User-Agent
        
        Returns:
            str: 随机的User-Agent字符串
        """
        user_agent = random.choice(self.USER_AGENTS)
        logger.debug(f"使用User-Agent: {user_agent[:50]}...")
        return user_agent
    
    def random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None):
        """
        执行随机延时
        
        Args:
            min_delay: 最小延时（可选，使用实例默认值）
            max_delay: 最大延时（可选，使用实例默认值）
        """
        min_d = min_delay if min_delay is not None else self.min_delay
        max_d = max_delay if max_delay is not None else self.max_delay
        
        delay_time = random.uniform(min_d, max_d)
        logger.debug(f"随机延时: {delay_time:.2f}秒")
        time.sleep(delay_time)
    
    def request_interval_control(self, min_interval: float = 1.0):
        """
        控制请求间隔
        
        Args:
            min_interval: 最小请求间隔（秒）
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.debug(f"请求间隔控制: 等待{wait_time:.2f}秒")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def adaptive_delay(self, base_delay: float = 2.0, error_count: int = 0):
        """
        自适应延时（根据错误次数调整）
        
        Args:
            base_delay: 基础延时
            error_count: 错误次数
        """
        # 根据错误次数增加延时
        multiplier = 1 + (error_count * 0.5)
        delay_time = base_delay * multiplier + random.uniform(0, 2)
        
        logger.info(f"自适应延时: {delay_time:.2f}秒 (错误次数: {error_count})")
        time.sleep(delay_time)
    
    def configure_browser_options(self, options) -> None:
        """
        配置浏览器选项以减少检测
        
        Args:
            options: 浏览器选项对象
        """
        try:
            # 设置随机User-Agent
            user_agent = self.get_random_user_agent()
            options.set_user_agent(user_agent)
            
            # 禁用自动化检测
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--disable-dev-shm-usage')
            options.set_argument('--no-sandbox')
            options.set_argument('--disable-gpu')
            
            # 设置窗口大小
            options.set_argument('--window-size=1920,1080')
            
            # 禁用图片加载（可选，提高速度）
            # options.set_argument('--disable-images')
            
            logger.info("浏览器反检测选项配置完成")
            
        except Exception as e:
            logger.warning(f"配置浏览器选项失败: {e}")
    
    def get_retry_delay(self, attempt: int, base_delay: float = 1.0) -> float:
        """
        获取重试延时（指数退避）
        
        Args:
            attempt: 重试次数（从1开始）
            base_delay: 基础延时
            
        Returns:
            float: 延时时间
        """
        # 指数退避 + 随机抖动
        delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
        max_delay = 30.0  # 最大延时30秒
        
        return min(delay, max_delay)
    
    def should_retry(self, attempt: int, max_attempts: int = 3) -> bool:
        """
        判断是否应该重试
        
        Args:
            attempt: 当前尝试次数
            max_attempts: 最大尝试次数
            
        Returns:
            bool: 是否应该重试
        """
        return attempt < max_attempts
    
    def log_request_stats(self):
        """记录请求统计信息"""
        logger.info(f"请求统计 - 总请求数: {self.request_count}")


class RetryManager:
    """重试管理器"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        """
        初始化重试管理器
        
        Args:
            max_attempts: 最大重试次数
            base_delay: 基础延时
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.anti_detection = AntiDetectionManager()
        
        logger.info(f"重试管理器初始化 - 最大重试: {max_attempts}次")
    
    def execute_with_retry(self, func, *args, **kwargs):
        """
        带重试机制执行函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 重试次数用尽后抛出最后一次异常
        """
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                logger.debug(f"执行尝试 {attempt}/{self.max_attempts}")
                result = func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"重试成功 - 第{attempt}次尝试")
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"第{attempt}次尝试失败: {e}")
                
                if attempt < self.max_attempts:
                    delay = self.anti_detection.get_retry_delay(attempt, self.base_delay)
                    logger.info(f"等待{delay:.2f}秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"重试次数用尽，最终失败")
        
        # 重试次数用尽，抛出最后一次异常
        raise last_exception


# 全局实例
anti_detection_manager = AntiDetectionManager()
retry_manager = RetryManager()


def get_anti_detection_manager() -> AntiDetectionManager:
    """获取反检测管理器实例"""
    return anti_detection_manager


def get_retry_manager() -> RetryManager:
    """获取重试管理器实例"""
    return retry_manager


def random_delay(min_delay: float = 2.0, max_delay: float = 5.0):
    """
    便捷函数：执行随机延时
    
    Args:
        min_delay: 最小延时
        max_delay: 最大延时
    """
    anti_detection_manager.random_delay(min_delay, max_delay)


def get_random_user_agent() -> str:
    """
    便捷函数：获取随机User-Agent
    
    Returns:
        str: 随机User-Agent
    """
    return anti_detection_manager.get_random_user_agent()