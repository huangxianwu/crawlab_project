#!/usr/bin/env python3
"""
滑块处理调试脚本
专门测试和调试滑块处理功能
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_debug_webdriver():
    """创建用于调试的WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # 不使用无头模式，便于观察
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver
    except Exception as e:
        print(f"WebDriver创建失败: {e}")
        return None

def debug_slider_detection():
    """调试滑块检测功能"""
    print("🔍 滑块处理调试")
    print("=" * 50)
    
    driver = create_debug_webdriver()
    if not driver:
        return False
    
    try:
        # 访问TikTok Shop搜索页面
        search_url = "https://www.tiktok.com/shop/s/phone%20case"
        print(f"🔄 访问页面: {search_url}")
        
        driver.get(search_url)
        time.sleep(5)
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ 当前URL: {current_url}")
        print(f"✅ 页面标题: {page_title}")
        
        # 导入滑块处理器
        from handlers.slider import SliderHandler
        slider_handler = SliderHandler(driver)
        
        print("\n🔄 步骤1: 检测滑块")
        
        # 详细的滑块检测
        page_source = driver.page_source
        print(f"页面内容长度: {len(page_source)} 字符")
        
        # 检查页面源码中的关键词
        captcha_keywords = ['captcha', 'slider', 'verify', '滑块', '验证', 'secsdk']
        found_keywords = []
        for keyword in captcha_keywords:
            if keyword in page_source.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"✅ 页面源码中发现验证码相关关键词: {found_keywords}")
        else:
            print("⚠️  页面源码中未发现验证码关键词")
        
        # 使用滑块处理器检测
        has_slider = slider_handler.detect_slider()
        print(f"滑块检测结果: {'检测到滑块' if has_slider else '未检测到滑块'}")
        
        # 获取详细的验证码状态
        captcha_status = slider_handler.get_captcha_status()
        print(f"验证码状态: {captcha_status}")
        
        if has_slider:
            print("\n🔄 步骤2: 分析滑块元素")
            
            # 查找滑块相关元素
            slider_selectors = [
                "#captcha_container",
                ".secsdk-captcha-drag-wrapper",
                ".secsdk-captcha-drag-icon",
                ".captcha-verify-image",
                "[class*='captcha']",
                "[id*='captcha']"
            ]
            
            found_elements = []
            for selector in slider_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        found_elements.append((selector, len(elements)))
                        print(f"  找到元素: {selector} ({len(elements)}个)")
                except:
                    pass
            
            if not found_elements:
                print("  ⚠️  未找到滑块相关元素")
            
            # 查找图片元素
            try:
                imgs = driver.find_elements(By.TAG_NAME, "img")
                captcha_imgs = []
                for img in imgs:
                    src = img.get_attribute('src') or ''
                    alt = img.get_attribute('alt') or ''
                    if 'captcha' in (src + alt).lower():
                        captcha_imgs.append(img)
                
                print(f"  找到验证码图片: {len(captcha_imgs)}个")
                
                if len(captcha_imgs) >= 2:
                    print("  ✅ 图片数量足够进行滑块识别")
                    
                    # 测试ddddocr
                    print("\n🔄 步骤3: 测试ddddocr")
                    try:
                        import ddddocr
                        det = ddddocr.DdddOcr(det=False, ocr=False)
                        print("  ✅ ddddocr初始化成功")
                        
                        # 尝试处理滑块
                        print("\n🔄 步骤4: 尝试处理滑块")
                        print("  注意观察浏览器中的滑块是否移动...")
                        
                        if slider_handler.solve_slider_captcha():
                            print("  ✅ 滑块处理成功")
                        else:
                            print("  ❌ 滑块处理失败")
                            
                            # 尝试备用方案
                            print("\n🔄 步骤5: 尝试备用方案")
                            if slider_handler.fallback_random_slide():
                                print("  ✅ 随机滑动成功")
                            else:
                                print("  ❌ 随机滑动失败")
                        
                    except ImportError:
                        print("  ❌ ddddocr未安装")
                    except Exception as e:
                        print(f"  ❌ ddddocr测试失败: {e}")
                
                else:
                    print("  ⚠️  验证码图片不足")
                    
            except Exception as e:
                print(f"  ❌ 查找图片元素失败: {e}")
        
        else:
            print("\n⚠️  未检测到滑块，可能的原因:")
            print("  1. 页面还在加载中")
            print("  2. 当前访问没有触发滑块验证")
            print("  3. 滑块元素选择器需要更新")
            print("  4. 页面结构发生了变化")
        
        # 保持浏览器打开供手动检查
        print(f"\n🔍 浏览器将保持打开60秒供手动检查...")
        print("请手动检查:")
        print("1. 页面是否显示了滑块验证")
        print("2. 滑块元素是否可见")
        print("3. 是否可以手动拖动滑块")
        
        for i in range(60, 0, -1):
            print(f"\r剩余时间: {i}秒", end="", flush=True)
            time.sleep(1)
        
        print("\n")
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        return False
    
    finally:
        driver.quit()
        print("✅ WebDriver已关闭")

def main():
    """主函数"""
    print("滑块处理功能调试")
    print("用于诊断滑块检测和处理问题")
    
    success = debug_slider_detection()
    
    if success:
        print("\n✅ 调试完成")
        print("请根据浏览器中观察到的情况判断滑块处理是否正常")
    else:
        print("\n❌ 调试失败")

if __name__ == "__main__":
    main()