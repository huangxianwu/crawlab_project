#!/usr/bin/env python3
"""
测试滑块处理备用方案
使用随机滑动来处理滑块验证
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_debug_webdriver():
    """创建用于调试的WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver
    except Exception as e:
        print(f"WebDriver创建失败: {e}")
        return None

def test_slider_fallback():
    """测试滑块处理备用方案"""
    print("🔍 测试滑块处理备用方案")
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
        
        # 检测滑块
        has_slider = slider_handler.detect_slider()
        print(f"滑块检测结果: {'检测到滑块' if has_slider else '未检测到滑块'}")
        
        if has_slider:
            print("\n🔄 尝试使用备用方案处理滑块")
            print("注意观察浏览器中的滑块是否移动...")
            
            # 直接使用备用方案
            if slider_handler.fallback_random_slide():
                print("✅ 随机滑动执行成功")
                
                # 等待一段时间看结果
                time.sleep(3)
                
                # 再次检测滑块
                if not slider_handler.detect_slider():
                    print("🎉 滑块验证成功！页面已跳转")
                else:
                    print("⚠️  滑块仍然存在，可能需要多次尝试")
            else:
                print("❌ 随机滑动执行失败")
            
            # 尝试完整的重试流程
            print("\n🔄 尝试完整的重试流程")
            if slider_handler.handle_captcha_with_retry():
                print("🎉 滑块处理重试成功！")
            else:
                print("⚠️  滑块处理重试失败")
        
        else:
            print("⚠️  未检测到滑块，无法测试处理功能")
        
        # 检查页面状态
        print(f"\n📋 最终页面状态:")
        final_url = driver.current_url
        final_title = driver.title
        print(f"URL: {final_url}")
        print(f"标题: {final_title}")
        
        # 保持浏览器打开供观察
        print(f"\n🔍 浏览器将保持打开30秒供观察结果...")
        for i in range(30, 0, -1):
            print(f"\r剩余时间: {i}秒", end="", flush=True)
            time.sleep(1)
        
        print("\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    finally:
        driver.quit()
        print("✅ WebDriver已关闭")

def main():
    """主函数"""
    print("滑块处理备用方案测试")
    print("测试随机滑动功能是否能处理滑块验证")
    
    success = test_slider_fallback()
    
    if success:
        print("\n✅ 测试完成")
        print("如果看到滑块移动并且页面发生变化，说明滑块处理功能正常")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()