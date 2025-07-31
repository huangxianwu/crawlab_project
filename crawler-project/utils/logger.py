"""
日志记录工具
提供统一的日志记录功能
"""
import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

from config import Config


def setup_logger(name: Optional[str] = None, 
                level: Optional[str] = None,
                log_file: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称，默认为'crawler'
        level: 日志级别，默认从配置读取
        log_file: 日志文件名，默认从配置读取
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 设置默认值
    if name is None:
        name = 'crawler'
    if level is None:
        level = Config.LOG_LEVEL
    if log_file is None:
        log_file = Config.LOG_FILE
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建日志目录
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt=Config.LOG_FORMAT,
        datefmt=Config.LOG_DATE_FORMAT
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器（带轮转）
    log_file_path = os.path.join(Config.LOG_DIR, log_file)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=Config.LOG_MAX_SIZE,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 记录初始化信息
    logger.info(f"日志系统初始化完成 - 级别: {level}, 文件: {log_file_path}")
    
    return logger


def get_logger(name: str = 'crawler') -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)


class CrawlerLogger:
    """爬虫专用日志记录器类"""
    
    def __init__(self, name: str = 'crawler'):
        self.logger = setup_logger(name)
        self.name = name
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def log_task_start(self, task_name: str, **kwargs):
        """记录任务开始"""
        self.info(f"任务开始: {task_name}", **kwargs)
    
    def log_task_end(self, task_name: str, success: bool = True, **kwargs):
        """记录任务结束"""
        status = "成功" if success else "失败"
        self.info(f"任务结束: {task_name} - {status}", **kwargs)
    
    def log_keyword_start(self, keyword: str):
        """记录关键词处理开始"""
        self.info(f"开始处理关键词: {keyword}")
    
    def log_keyword_end(self, keyword: str, count: int):
        """记录关键词处理结束"""
        self.info(f"关键词处理完成: {keyword}, 采集数量: {count}")
    
    def log_slider_detected(self):
        """记录检测到滑块"""
        self.warning("检测到滑块验证")
    
    def log_slider_solved(self, success: bool):
        """记录滑块处理结果"""
        status = "成功" if success else "失败"
        self.info(f"滑块处理{status}")
    
    def log_database_operation(self, operation: str, count: int = 0, success: bool = True):
        """记录数据库操作"""
        status = "成功" if success else "失败"
        if count > 0:
            self.info(f"数据库{operation}{status}: {count}条记录")
        else:
            self.info(f"数据库{operation}{status}")
    
    def log_error_with_traceback(self, message: str, exception: Exception):
        """记录带堆栈跟踪的错误"""
        import traceback
        error_msg = f"{message}: {str(exception)}\n{traceback.format_exc()}"
        self.error(error_msg)
    
    def _format_message(self, message: str, **kwargs) -> str:
        """格式化日志消息"""
        if kwargs:
            # 添加额外的上下文信息
            context_parts = []
            for key, value in kwargs.items():
                context_parts.append(f"{key}={value}")
            
            if context_parts:
                context_str = " | ".join(context_parts)
                return f"{message} | {context_str}"
        
        return message


# 创建全局日志记录器实例
crawler_logger = CrawlerLogger()


def log_function_call(func):
    """
    装饰器：记录函数调用
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        logger.debug(f"调用函数: {func_name}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数执行成功: {func_name}")
            return result
        except Exception as e:
            logger.error(f"函数执行失败: {func_name} - {str(e)}")
            raise
    
    return wrapper


def log_execution_time(func):
    """
    装饰器：记录函数执行时间
    """
    def wrapper(*args, **kwargs):
        import time
        logger = get_logger()
        func_name = func.__name__
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"函数执行时间: {func_name} - {execution_time:.2f}秒")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"函数执行失败: {func_name} - {execution_time:.2f}秒 - {str(e)}")
            raise
    
    return wrapper


# 便捷的日志记录函数
def log_info(message: str, **kwargs):
    """记录信息日志"""
    crawler_logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """记录警告日志"""
    crawler_logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """记录错误日志"""
    crawler_logger.error(message, **kwargs)


def log_debug(message: str, **kwargs):
    """记录调试日志"""
    crawler_logger.debug(message, **kwargs)