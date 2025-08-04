#!/usr/bin/env python3
"""
基于DrissionPage的滑块处理器
直接采用参考项目的完整技术方案
技术栈: DrissionPage + ddddocr (与参考项目完全一致)
"""
import time
import random
import requests
import numpy as np
from typing import Optional
from DrissionPage import ChromiumPage, ChromiumOptions

# 延迟导入OpenCV，避免系统依赖问题
def get_cv2():
    """延迟导入cv2，避免在模块加载时就失败"""
    try:
        import cv2
        return cv2
    except ImportError as e:
        print(f"Warning: OpenCV导入失败: {e}")
        return None

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
except ImportError:
    DDDDOCR_AVAILABLE = False

class DrissionPageSliderHandler:
    """
    基于DrissionPage的滑块处理器
    直接移植参考项目的成功实现
    """
    
    def __init__(self, proxy_enabled=False, proxy_host="127.0.0.1", proxy_port="10809"):
        self.page = None
        self.det = None
        self.proxy_enabled = proxy_enabled
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        
        # 初始化浏览器和OCR
        self.init_browser()
        self.init_ocr()
    
    def init_browser(self):
        """初始化浏览器 - 完全按照参考项目的方式"""
        try:
            print("🌐 正在启动Chrome浏览器...")
            co = ChromiumOptions()
            
            # 添加稳定性参数
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-web-security')
            co.set_argument('--allow-running-insecure-content')
            
            # 设置代理 - 参考项目的代理配置
            if self.proxy_enabled:
                proxy_address = f"http://{self.proxy_host}:{self.proxy_port}"
                co.set_proxy(proxy_address)
                print(f"🔗 已设置代理: {proxy_address}")
            
            # 创建页面实例 - 参考项目的配置
            self.page = ChromiumPage(co)
            
            # 设置用户代理和加载模式
            self.page.set.user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36")
            self.page.set.load_mode.eager()
            
            print("✅ 浏览器初始化完成")
            
        except Exception as e:
            raise Exception(f"初始化浏览器失败: {e}")
    
    def init_ocr(self):
        """初始化OCR和滑块检测器 - 参考项目的方式"""
        try:
            print("🔍 正在初始化验证码识别...")
            if DDDDOCR_AVAILABLE:
                self.det = ddddocr.DdddOcr(det=False, ocr=False)
                print("✅ ddddocr滑块检测器初始化成功")
            else:
                raise Exception("ddddocr未安装")
                
        except Exception as e:
            raise Exception(f"初始化验证码识别失败: {e}")
    
    def navigate_to_url(self, url: str):
        """导航到指定URL"""
        try:
            print(f"🔄 访问页面: {url}")
            
            # 使用更稳定的导航方式
            self.page.get(url)
            time.sleep(5)  # 增加等待时间
            
            # 检查页面是否加载成功
            current_url = self.page.url
            current_title = self.page.title
            
            if not current_url or current_url == "data:,":
                raise Exception("页面加载失败，URL为空")
            
            print(f"✅ 当前URL: {current_url}")
            print(f"✅ 页面标题: {current_title}")
            
            return current_url, current_title
            
        except Exception as e:
            raise Exception(f"页面导航失败: {e}")
    
    def handle_captcha(self, page=None) -> bool:
        """
        处理验证码 - 直接移植参考项目的 handle_captcha 方法
        完全按照参考项目的逻辑实现
        """
        if page is None:
            page = self.page
        
        try:
            # 多次检查验证码，增加成功率 - 参考项目的重试机制
            for attempt in range(3):
                html_text = page.html
                
                # 检查是否有验证码 - 参考项目的检测方法
                has_captcha_container = '<div id="captcha_container">' in html_text
                has_security_check = "Security Check" in page.title
                
                print(f"验证码容器检测: {has_captcha_container}")
                print(f"安全检查页面: {has_security_check}")
                
                if not has_captcha_container and not has_security_check:
                    return False
                
                if not has_captcha_container:
                    print("⚠️ 未找到captcha_container，但页面显示Security Check，继续处理")
                
                if attempt == 0:
                    print("🔐 检测到验证码，正在处理...")
                else:
                    print(f"🔄 验证码处理重试 {attempt + 1}/3")
                
                # 查找验证码图片 - 参考项目的方法
                imgs = page.eles("tag=img", timeout=20)
                print(f"页面总共找到 {len(imgs)} 张图片")
                
                # 筛选显示的图片
                visible_imgs = []
                for i, img in enumerate(imgs):
                    try:
                        if img.states.is_displayed:
                            src = img.attr("src") or ''
                            size = img.rect.size
                            print(f"图片 {i+1}: src={src[:50]}..., size={size}")
                            if size[0] > 50 and size[1] > 50:  # 过滤太小的图片
                                visible_imgs.append(img)
                    except:
                        continue
                
                print(f"筛选出 {len(visible_imgs)} 张可见的验证码图片")
                
                if len(visible_imgs) < 2:
                    print("⚠️ 验证码图片不足")
                    continue
                
                # 使用筛选后的图片
                imgs = visible_imgs
                
                try:
                    # 获取验证码图片URL - 参考项目的方式
                    background_img_url = imgs[0].attr("src")
                    target_img_url = imgs[1].attr("src")
                    
                    print(f"背景图URL: {background_img_url[:50]}...")
                    print(f"滑块图URL: {target_img_url[:50]}...")
                    
                    # 下载验证码图片 - 参考项目的下载方式
                    proxies = self.get_proxies()
                    background_response = requests.get(background_img_url, proxies=proxies, timeout=10)
                    target_response = requests.get(target_img_url, proxies=proxies, timeout=10)
                    
                    if background_response.status_code == 200 and target_response.status_code == 200:
                        # 使用ddddocr的滑块匹配功能 - 参考项目的核心算法
                        background_bytes = background_response.content
                        target_bytes = target_response.content
                        
                        # 使用滑块检测器识别位置 - 参考项目的识别逻辑
                        try:
                            res = self.det.slide_match(target_bytes, background_bytes)
                            if res and "target" in res:
                                target_x = res["target"][0]
                                print(f"🎯 识别到滑块位置: {target_x}")
                                
                                # 计算滑块位置的偏移量 - 参考项目的关键算法
                                x_offset = imgs[1].rect.location[0] - imgs[0].rect.location[0]
                                
                                # 获取图片尺寸进行缩放 - 参考项目的精确算法
                                img_array = np.frombuffer(background_bytes, dtype=np.uint8)
                                cv2 = get_cv2()
                                if cv2:
                                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                                else:
                                    img = None
                                if img is not None:
                                    height, width = img.shape[:2]
                                    # 按比例缩放到实际滑块位置 - 参考项目的关键算法
                                    actual_x = target_x * (340 / width) - x_offset
                                    print(f"📐 图片原始尺寸: {width}x{height}")
                                    print(f"📐 缩放比例: {340/width}")
                                    print(f"📐 位置偏移: {x_offset}")
                                    print(f"📐 计算的实际滑动距离: {actual_x}")
                                else:
                                    actual_x = target_x - x_offset
                                    print(f"📐 使用原始坐标: {actual_x}")
                                
                                # 执行滑动操作 - 参考项目的滑动方法
                                slider_element = page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=5)
                                if slider_element:
                                    print(f"✅ 找到滑块元素，开始拖拽")
                                    print(f"🎯 拖拽参数: 水平={actual_x}, 垂直=10, 持续时间=0.2秒")
                                    
                                    # 直接使用参考项目的drag方法
                                    slider_element.drag(actual_x, 10, 0.2)
                                    time.sleep(3)
                                    
                                    # 检查验证码是否通过 - 参考项目的验证方式
                                    new_html = page.html
                                    if "captcha-verify-image" not in new_html:
                                        print("✅ 验证码处理成功")
                                        return False  # 返回False表示无验证码
                                    else:
                                        print("⚠️ 验证码未通过，准备重试")
                                else:
                                    print("⚠️ 未找到滑块元素")
                            else:
                                print("⚠️ 滑块位置识别失败")
                                
                        except Exception as e:
                            print(f"⚠️ 滑块识别异常: {e}")
                            # 如果滑块识别失败，使用随机位移作为备选方案 - 参考项目的备选方案
                            slide_distance = random.randint(100, 200)
                            print(f"🎲 使用随机滑动距离: {slide_distance}")
                            slider_element = page.ele("xpath://*[@id='secsdk-captcha-drag-wrapper']/div[2]", timeout=5)
                            if slider_element:
                                slider_element.drag(slide_distance, 10, 0.2)
                                time.sleep(3)
                    
                    # 等待一段时间再重试 - 参考项目的重试逻辑
                    if attempt < 2:
                        time.sleep(2)
                        page.refresh(ignore_cache=True)
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"⚠️ 验证码处理异常: {e}")
                    continue
            
            # 所有尝试都失败了
            print("❌ 验证码处理失败，已尝试3次")
            return True  # 返回True表示有验证码但处理失败
            
        except Exception as e:
            print(f"❌ 滑块处理异常: {e}")
            return True
    
    def get_proxies(self) -> Optional[dict]:
        """获取代理设置 - 参考项目的代理配置"""
        if self.proxy_enabled:
            proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        return None
    
    def test_slider_handling(self, url: str) -> bool:
        """测试滑块处理功能"""
        try:
            # 导航到目标页面
            current_url, current_title = self.navigate_to_url(url)
            
            # 检查是否需要滑块验证
            if "Security Check" not in current_title:
                print("✅ 无需滑块验证，直接访问成功")
                return True
            
            print("🔍 检测到滑块验证页面，开始处理...")
            
            # 处理滑块验证
            start_time = time.time()
            has_captcha = self.handle_captcha()
            end_time = time.time()
            
            print(f"处理耗时: {end_time - start_time:.2f} 秒")
            
            if not has_captcha:
                print("🎉 滑块处理成功！")
                
                # 检查最终状态
                final_url = self.page.url
                final_title = self.page.title
                
                print(f"✅ 最终URL: {final_url}")
                print(f"✅ 最终标题: {final_title}")
                
                if final_url != current_url or "Security Check" not in final_title:
                    print("🎊 验证成功！页面已跳转到搜索结果")
                    return True
                else:
                    print("⚠️  页面未跳转，但滑块处理报告成功")
                    return True
            else:
                print("❌ 滑块处理失败")
                return False
                
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.page:
                self.page.quit()
                print("✅ 浏览器已关闭")
        except:
            print("⚠️  浏览器可能已经关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()