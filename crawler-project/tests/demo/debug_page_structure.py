#!/usr/bin/env python3
"""
调试页面结构
分析TikTok页面的实际数据结构
"""
import os
import sys
import time
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from drissionpage_slider_handler import DrissionPageSliderHandler

def debug_page_structure():
    """调试页面结构"""
    print("🔍 调试TikTok页面结构")
    print("=" * 60)
    
    with DrissionPageSliderHandler() as handler:
        # 访问搜索页面
        search_url = "https://www.tiktok.com/shop/s/phone%20case"
        handler.navigate_to_url(search_url)
        
        # 处理滑块
        if handler.handle_captcha():
            print("❌ 滑块处理失败")
            return
        
        print("✅ 滑块处理成功，开始分析页面结构")
        
        # 查找页面数据元素
        try:
            ele = handler.page.ele("@id=__MODERN_ROUTER_DATA__", timeout=10)
            if not ele:
                print("❌ 未找到 __MODERN_ROUTER_DATA__ 元素")
                return
            
            # 解析JSON数据
            loader_data = json.loads(ele.inner_html)
            
            print("✅ 找到页面数据，分析结构...")
            print(f"📊 顶级键: {list(loader_data.keys())}")
            
            if "loaderData" in loader_data:
                loader_keys = list(loader_data["loaderData"].keys())
                print(f"📊 loaderData键: {loader_keys}")
                
                # 分析每个键的结构
                for key in loader_keys:
                    print(f"\n🔍 分析键: {key}")
                    data = loader_data["loaderData"][key]
                    
                    if isinstance(data, dict):
                        print(f"  子键: {list(data.keys())}")
                        
                        # 查找page_config
                        if "page_config" in data:
                            page_config = data["page_config"]
                            print(f"  page_config键: {list(page_config.keys())}")
                            
                            # 查找components_map
                            if "components_map" in page_config:
                                components_map = page_config["components_map"]
                                print(f"  ✅ 找到components_map: {len(components_map)} 个组件")
                                
                                # 分析组件
                                for i, component in enumerate(components_map[:3]):  # 只看前3个
                                    comp_name = component.get("component_name", "未知")
                                    comp_type = component.get("component_type", "未知")
                                    print(f"    组件{i+1}: {comp_name} (类型: {comp_type})")
                                    
                                    # 查找商品数据
                                    if "component_data" in component:
                                        comp_data = component["component_data"]
                                        if "products" in comp_data:
                                            products = comp_data["products"]
                                            print(f"      ✅ 找到商品数据: {len(products)} 个商品")
                                            
                                            # 显示第一个商品的结构
                                            if products:
                                                first_product = products[0]
                                                print(f"      商品字段: {list(first_product.keys())}")
                                                print(f"      商品ID: {first_product.get('product_id', '无')}")
                                                print(f"      商品标题: {first_product.get('title', '无')}")
                            else:
                                print("  ❌ 未找到components_map")
                        else:
                            print("  ❌ 未找到page_config")
                    else:
                        print(f"  数据类型: {type(data)}")
            
            # 保存完整数据到文件供分析
            with open("page_structure_debug.json", "w", encoding="utf-8") as f:
                json.dump(loader_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 完整页面数据已保存到: page_structure_debug.json")
            
        except Exception as e:
            print(f"❌ 分析页面结构失败: {e}")

if __name__ == "__main__":
    debug_page_structure()