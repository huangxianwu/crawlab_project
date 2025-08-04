#!/usr/bin/env python3
"""
Crawlab环境专用爬虫启动器
处理Crawlab特有的环境变量和参数传递
"""
import os
import sys

def setup_crawlab_environment():
    """设置Crawlab环境变量"""
    # Crawlab数据库配置
    if not os.getenv("MONGO_URI"):
        # 构建Crawlab标准的MongoDB连接字符串
        mongo_host = os.getenv("CRAWLAB_MONGO_HOST", "mongo")
        mongo_port = os.getenv("CRAWLAB_MONGO_PORT", "27017")
        mongo_db = os.getenv("CRAWLAB_MONGO_DB", "crawlab_test")
        
        os.environ["MONGO_URI"] = f"mongodb://{mongo_host}:{mongo_port}"
        os.environ["DATABASE_NAME"] = mongo_db
        os.environ["COLLECTION_NAME"] = "products"
    
    # 从Crawlab任务参数获取配置
    keywords = os.getenv("keywords", "phone case")
    max_pages = os.getenv("max_pages", "1")
    headless = os.getenv("headless", "true")
    
    print("🔧 Crawlab环境配置:")
    print(f"  MongoDB: {os.getenv('MONGO_URI')}")
    print(f"  数据库: {os.getenv('DATABASE_NAME')}")
    print(f"  集合: {os.getenv('COLLECTION_NAME')}")
    print(f"  关键词: {keywords}")
    print(f"  最大页数: {max_pages}")
    print(f"  无头模式: {headless}")
    print()
    
    return keywords, max_pages, headless

def main():
    """主函数"""
    print("🚀 Crawlab爬虫启动器")
    print("=" * 50)
    
    # 设置环境
    keywords, max_pages, headless = setup_crawlab_environment()
    
    # 导入并运行简化版爬虫
    try:
        from crawlab_simple_runner import SimpleCrawlabCrawler
        
        crawler = SimpleCrawlabCrawler()
        crawler.run(keywords, int(max_pages))
        
    except ImportError as e:
        print(f"❌ 导入爬虫模块失败: {e}")
        print("尝试直接执行简化版爬虫...")
        
        # 如果导入失败，直接执行简化版爬虫文件
        import subprocess
        result = subprocess.run([sys.executable, "crawlab_simple_runner.py"], 
                              capture_output=False)
        sys.exit(result.returncode)
    
    except Exception as e:
        print(f"❌ 爬虫运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()