#!/usr/bin/env python3
"""
测试基于DrissionPage的滑块处理器
直接采用参考项目的完整技术方案
"""
import os
import sys
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from drissionpage_slider_handler import DrissionPageSliderHandler

def test_drissionpage_slider():
    """测试DrissionPage滑块处理器"""
    print("🚀 DrissionPage滑块处理器测试")
    print("直接采用参考项目的完整技术方案")
    print("技术栈: DrissionPage + ddddocr")
    print("=" * 60)
    
    # 创建滑块处理器
    try:
        with DrissionPageSliderHandler() as slider_handler:
            # 测试TikTok Shop滑块处理
            search_url = "https://www.tiktok.com/shop/s/phone%20case"
            
            print(f"🎯 开始测试滑块处理...")
            success = slider_handler.test_slider_handling(search_url)
            
            if success:
                print("\n🎉 测试成功！")
                print("DrissionPage方案工作正常")
                
                # 保持浏览器打开观察
                print(f"\n🔍 浏览器将保持打开30秒供观察...")
                for i in range(30, 0, -1):
                    print(f"\r剩余时间: {i}秒", end="", flush=True)
                    time.sleep(1)
                print("\n")
                
                return True
            else:
                print("\n❌ 测试失败！")
                return False
                
    except Exception as e:
        print(f"❌ 创建滑块处理器失败: {e}")
        return False

def main():
    """主函数"""
    print("TikTok滑块处理 - DrissionPage完整方案")
    print("直接采用参考项目的验证过的技术栈")
    print("\n🔧 技术优势:")
    print("- ✅ 与参考项目完全一致的技术栈")
    print("- ✅ 经过验证的成功算法")
    print("- ✅ 原生的drag操作支持")
    print("- ✅ 更高的成功率和稳定性")
    print("- ✅ 无需复杂的API适配")
    
    success = test_drissionpage_slider()
    
    if success:
        print("\n🎉 DrissionPage方案验证成功！")
        print("建议采用此方案替代Selenium实现")
        print("\n📋 下一步:")
        print("1. 将DrissionPage集成到主爬虫项目")
        print("2. 替换现有的Selenium滑块处理")
        print("3. 享受更高的滑块处理成功率")
    else:
        print("\n❌ DrissionPage方案测试失败")
        print("需要检查环境配置或网络连接")

if __name__ == "__main__":
    main()