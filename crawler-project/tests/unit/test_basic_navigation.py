#!/usr/bin/env python3
"""
测试基本的页面导航功能
排查WebDriver导航问题
"""
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_basic_navigation():
    """测试基本的页面导航"""
    print("🔍 测试基本页面导航功能")
    print("=" * 50)
    
    driver = None
    
    try:
        # 创建简化的Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 创建WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ WebDriver创建成功")
        
        # 设置超时
        driver.set_page_load_timeout(30)
        
        # 测试1: 访问Google（基础测试）
        print("\n🔄 测试1: 访问Google")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ 当前URL: {current_url}")
        print(f"✅ 页面标题: {page_title}")
        
        if "google" in current_url.lower():
            print("✅ Google访问成功")
        else:
            print("❌ Google访问失败")
            return False
        
        # 测试2: 访问TikTok主页
        print("\n🔄 测试2: 访问TikTok主页")
        driver.get("https://www.tiktok.com")
        time.sleep(5)  # TikTok需要更长的加载时间
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ 当前URL: {current_url}")
        print(f"✅ 页面标题: {page_title}")
        
        if "tiktok" in current_url.lower():
            print("✅ TikTok主页访问成功")
        else:
            print("❌ TikTok主页访问失败")
        
        # 测试3: 访问TikTok Shop
        print("\n🔄 测试3: 访问TikTok Shop")
        shop_url = "https://www.tiktok.com/shop"
        driver.get(shop_url)
        time.sleep(5)
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ 当前URL: {current_url}")
        print(f"✅ 页面标题: {page_title}")
        
        if "shop" in current_url.lower() or "tiktok" in current_url.lower():
            print("✅ TikTok Shop访问成功")
        else:
            print("❌ TikTok Shop访问失败")
        
        # 测试4: 访问TikTok Shop搜索页面
        print("\n🔄 测试4: 访问TikTok Shop搜索页面")
        search_url = "https://www.tiktok.com/shop/s/phone%20case"
        driver.get(search_url)
        time.sleep(5)
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"✅ 当前URL: {current_url}")
        print(f"✅ 页面标题: {page_title}")
        
        # 检查页面内容
        page_source = driver.page_source
        print(f"✅ 页面内容长度: {len(page_source)} 字符")
        
        if len(page_source) > 1000:  # 有实际内容
            print("✅ 页面有实际内容")
            
            # 检查是否有验证码或安全检查
            if "security check" in page_source.lower():
                print("⚠️  检测到安全检查页面")
            elif "captcha" in page_source.lower():
                print("⚠️  检测到验证码页面")
            elif "phone case" in page_source.lower():
                print("✅ 页面包含搜索关键词")
            else:
                print("⚠️  页面内容未知")
        else:
            print("❌ 页面内容为空或过少")
        
        # 保持浏览器打开一段时间供观察
        print(f"\n🔍 浏览器将保持打开30秒供手动检查...")
        print("请检查浏览器中显示的内容")
        
        for i in range(30, 0, -1):
            print(f"\r剩余时间: {i}秒", end="", flush=True)
            time.sleep(1)
        
        print("\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    finally:
        if driver:
            driver.quit()
            print("✅ WebDriver已关闭")

def main():
    """主函数"""
    print("WebDriver基本导航测试")
    print("排查页面导航问题")
    
    success = test_basic_navigation()
    
    if success:
        print("\n✅ 基本导航测试完成")
        print("如果看到了正确的页面内容，说明导航功能正常")
    else:
        print("\n❌ 基本导航测试失败")
        print("需要检查网络连接或WebDriver配置")

if __name__ == "__main__":
    main()