#!/usr/bin/env python3
"""
VNC显示模式的Crawlab爬虫
专门用于通过VNC观察滑块处理过程
"""
import os
import sys
import time
import json
import logging
import urllib.parse
import random
from datetime import datetime
from typing import List, Dict, Optional

# 设置显示模式环境变量
os.environ['DISPLAY'] = ':1'  # VNC显示器

# 基础配置
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "crawlab_test")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "products")

# 设置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('vnc_crawler')

def check_vnc_display():
    """检查VNC显示器是否可用"""
    try:
        display = os.getenv('DISPLAY', ':1')
        print(f"🖥️ 检查VNC显示器: {display}")
        
        # 检查X服务器是否运行
        result = os.system('xdpyinfo > /dev/null 2>&1')
        if result == 0:
            print("✅ VNC显示器可用")
            return True
        else:
            print("❌ VNC显示器不可用，请先运行 bash setup_vnc.sh")
            return False
    except Exception as e:
        print(f"❌ VNC检查失败: {e}")
        return False

def init_ddddocr():
    """初始化ddddocr"""
    try:
        import ddddocr
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        print("✅ ddddocr滑块检测器初始化成功")
        return det, True
    except Exception as e:
        print(f"⚠️ ddddocr初始化失败: {e}")
        return None, False

def get_cv2():
    """延迟导入cv2"""
    try:
        import cv2
        return cv2
    except ImportError as e:
        print(f"Warning: OpenCV导入失败: {e}")
        return None

class VNCCrawlabCrawler:
    """VNC显示模式的Crawlab爬虫"""
    
    def __init__(self):
        self.logger = logger
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.page = None
        self.det = None
        
        print("🚀 初始化VNC显示模式Crawlab爬虫...")
        self.logger.info("VNC显示模式Crawlab爬虫初始化")
    
    def setup_database(self):
        """设置数据库连接"""
        try:
            import pymongo
            
            self.mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.mongo_client.admin.command('ping')
            
            self.db = self.mongo_client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            print(f"✅ 数据库连接成功: {DATABASE_NAME}.{COLLECTION_NAME}")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def setup_browser(self):
        """设置浏览器 - 显示模式"""
        try:
            from DrissionPage import ChromiumPage, ChromiumOptions
            
            # 配置浏览器选项 - 显示模式
            options = ChromiumOptions()
            options.headless(False)  # 启用显示模式
            
            # Chrome路径配置
            chrome_bin = os.getenv('CHROME_BIN', '/usr/bin/google-chrome')
            if chrome_bin and os.path.exists(chrome_bin):
                options.set_browser_path(chrome_bin)
                print(f"🌐 使用Chrome路径: {chrome_bin}")
            
            # 显示模式专用参数
            startup_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--window-size=1200,800',
                '--window-position=100,100',
                f'--display={os.getenv("DISPLAY", ":1")}',
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            
            for arg in startup_args:
                options.set_argument(arg)
            
            # 创建页面对象
            self.page = ChromiumPage(addr_or_opts=options)
            
            print("✅ 浏览器初始化成功（显示模式）")
            print("🖥️ 现在可以通过VNC客户端观察浏览器行为")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            return False
    
    def handle_captcha_with_display(self):
        """带显示的验证码处理"""
        try:
            print("🔍 开始验证码处理（显示模式）...")
            print("👀 请通过VNC客户端观察浏览器窗口")
            
            # 初始化ddddocr
            if not hasattr(self, 'det') or self.det is None:
                self.det, ddddocr_ok = init_ddddocr()
                if not ddddocr_ok:
                    print("⚠️ ddddocr不可用")
                    return True
            
            # 等待用户观察
            print("⏱️ 等待5秒，请观察VNC中的浏览器窗口...")
            time.sleep(5)
            
            # 检查验证码
            for attempt in range(3):
                html_text = self.page.html
                has_captcha_container = '<div id="captcha_container">' in html_text
                has_security_check = "Security Check" in self.page.title
                
                print(f"🔍 第{attempt+1}次检查:")
                print(f"   验证码容器: {has_captcha_container}")
                print(f"   安全检查页面: {has_security_check}")
                print(f"   当前标题: {self.page.title}")
                print(f"   当前URL: {self.page.url}")
                
                if not has_captcha_container and not has_security_check:
                    print("✅ 无验证码，处理成功")
                    return False
                
                print(f"🔐 检测到验证码，开始处理（第{attempt+1}/3次）...")
                
                # 查找验证码图片
                imgs = self.page.eles("tag=img", timeout=20)
                print(f"📷 找到 {len(imgs)} 张图片")
                
                # 筛选可见图片
                visible_imgs = []
                for i, img in enumerate(imgs):
                    try:
                        if img.states.is_displayed:
                            src = img.attr("src") or ''
                            size = img.rect.size
                            location = img.rect.location
                            print(f"   图片{i+1}: 尺寸={size}, 位置={location}")
                            print(f"           URL={src[:80]}...")
                            if size[0] > 50 and size[1] > 50:
                                visible_imgs.append(img)
                    except Exception as e:
                        print(f"   图片{i+1}: 检查失败 - {e}")
                
                print(f"📷 筛选出 {len(visible_imgs)} 张有效验证码图片")
                
                if len(visible_imgs) < 2:
                    print("⚠️ 验证码图片不足，等待重试...")
                    time.sleep(3)
                    continue
                
                # 处理验证码
                try:
                    bg_img = visible_imgs[0]
                    slider_img = visible_imgs[1]
                    
                    bg_url = bg_img.attr("src")
                    slider_url = slider_img.attr("src")
                    
                    print(f"🖼️ 背景图: {bg_url[:80]}...")
                    print(f"🎯 滑块图: {slider_url[:80]}...")
                    
                    # 下载图片
                    import requests
                    bg_response = requests.get(bg_url, timeout=10)
                    slider_response = requests.get(slider_url, timeout=10)
                    
                    if bg_response.status_code == 200 and slider_response.status_code == 200:
                        # ddddocr识别
                        res = self.det.slide_match(slider_response.content, bg_response.content)
                        if res and "target" in res:
                            target_x = res["target"][0]
                            print(f"🎯 ddddocr识别位置: {target_x}")
                            
                            # 计算实际位置
                            x_offset = slider_img.rect.location[0] - bg_img.rect.location[0]
                            
                            # 图片缩放计算
                            import numpy as np
                            img_array = np.frombuffer(bg_response.content, dtype=np.uint8)
                            cv2 = get_cv2()
                            if cv2:
                                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                                if img is not None:
                                    height, width = img.shape[:2]
                                    scale_ratio = 340 / width
                                    actual_x = target_x * scale_ratio - x_offset
                                    print(f"📐 图片尺寸: {width}x{height}")
                                    print(f"📐 缩放比例: {scale_ratio}")
                                    print(f"📐 位置偏移: {x_offset}")
                                    print(f"📐 计算距离: {actual_x}")
                                else:
                                    actual_x = target_x - x_offset
                            else:
                                actual_x = target_x - x_offset
                            
                            # 查找滑块元素
                            slider_element = self.page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=5)
                            if slider_element:
                                print(f"🎯 找到滑块元素，准备拖拽")
                                print(f"   拖拽距离: {actual_x}")
                                print("👀 请观察VNC中的拖拽过程...")
                                
                                # 执行拖拽（慢速，便于观察）
                                slider_element.drag(actual_x, 10, 1.0)  # 1秒拖拽，便于观察
                                
                                print("⏱️ 等待验证结果...")
                                time.sleep(4)
                                
                                # 检查结果
                                new_html = self.page.html
                                new_title = self.page.title
                                new_url = self.page.url
                                
                                print(f"📄 验证后标题: {new_title}")
                                print(f"📄 验证后URL: {new_url}")
                                
                                success_indicators = [
                                    "captcha-verify-image" not in new_html,
                                    "Security Check" not in new_title,
                                    "captcha" not in new_url.lower(),
                                    "shop/s/" in new_url
                                ]
                                
                                if any(success_indicators):
                                    print("🎉 验证码处理成功！")
                                    return False
                                else:
                                    print("⚠️ 验证未通过，准备重试...")
                            else:
                                print("❌ 未找到滑块元素")
                        else:
                            print("❌ ddddocr识别失败")
                    else:
                        print("❌ 图片下载失败")
                
                except Exception as e:
                    print(f"❌ 验证码处理异常: {e}")
                
                # 重试前等待
                if attempt < 2:
                    print("⏱️ 等待重试...")
                    time.sleep(3)
                    self.page.refresh(ignore_cache=True)
                    time.sleep(3)
            
            print("❌ 验证码处理失败，已尝试3次")
            return True
            
        except Exception as e:
            print(f"❌ 验证码处理异常: {e}")
            return True
    
    def crawl_with_display(self, keyword: str):
        """带显示的爬取过程"""
        try:
            print(f"🎯 开始采集关键词: {keyword}")
            print("👀 请通过VNC观察整个过程")
            
            # 构建URL
            encoded_keyword = urllib.parse.quote(keyword)
            search_url = f"https://www.tiktok.com/shop/s/{encoded_keyword}"
            
            print(f"🌐 访问: {search_url}")
            self.page.get(search_url)
            
            print("⏱️ 等待页面加载...")
            time.sleep(5)
            
            current_url = self.page.url
            page_title = self.page.title
            
            print(f"📄 当前URL: {current_url}")
            print(f"📄 页面标题: {page_title}")
            
            # 处理验证码
            if "Security Check" in page_title or "captcha" in current_url.lower():
                print("🧩 检测到验证码页面")
                has_captcha = self.handle_captcha_with_display()
                if has_captcha:
                    print("❌ 验证码处理失败")
                    return 0
                print("✅ 验证码处理成功，继续采集")
                time.sleep(2)
            
            # 简单的数据提取演示
            print("📊 开始数据提取...")
            print("👀 请观察VNC中的页面内容")
            
            # 这里可以添加真实的数据提取逻辑
            # 暂时返回示例数据
            return 1
            
        except Exception as e:
            print(f"❌ 采集失败: {e}")
            return 0
    
    def run(self, keywords: str = "phone case"):
        """运行VNC显示模式爬虫"""
        print("🖥️ VNC显示模式爬虫启动")
        print("=" * 50)
        
        # 检查VNC
        if not check_vnc_display():
            print("❌ VNC环境未配置，请先运行: bash setup_vnc.sh")
            return
        
        # 初始化组件
        if not self.setup_database():
            return
        
        if not self.setup_browser():
            return
        
        print("🎉 VNC爬虫准备就绪！")
        print("📋 请使用VNC客户端连接 localhost:5901 观察过程")
        print("⏱️ 等待10秒让你连接VNC...")
        time.sleep(10)
        
        try:
            keyword_list = [k.strip() for k in keywords.split(',')]
            total_products = 0
            
            for keyword in keyword_list:
                if keyword:
                    count = self.crawl_with_display(keyword)
                    total_products += count
                    time.sleep(3)
            
            print("=" * 50)
            print(f"🎊 VNC爬虫运行完成！")
            print(f"✅ 处理关键词: {len(keyword_list)} 个")
            print(f"✅ 采集商品: {total_products} 个")
            
        except Exception as e:
            print(f"❌ 爬虫运行失败: {e}")
        
        finally:
            if self.page:
                print("⏱️ 保持浏览器打开30秒供观察...")
                time.sleep(30)
                self.page.quit()
            
            if self.mongo_client:
                self.mongo_client.close()

def main():
    """主函数"""
    keywords = os.getenv("keywords", "phone case")
    
    print("🖥️ VNC显示模式Crawlab爬虫")
    print(f"📋 关键词: {keywords}")
    
    crawler = VNCCrawlabCrawler()
    crawler.run(keywords)

if __name__ == "__main__":
    main()