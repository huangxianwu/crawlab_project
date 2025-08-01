#!/usr/bin/env python3
"""
基于参考项目成功算法的增强滑块处理
实现TikTok滑块验证的精确处理
"""
import os
import sys
import time
import random
import requests
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
ns
from sely
from selenium.webdriver.common.action_chains import ActionCains
erManager

# 添加项目路径
sys.pathe__)))

try:
    import dddocr
    DDDDOCR_AVAILABLE = True
    print("✅ ddddocr可用")
except ImportError:
    DDDDOCR_AVAILABLE = False
    print("❌ ddddocr不可用")

class EnhancedSli
    """基于参考项目成功算法的增强滑块处理器"""
    
    def __init__(self, driver):
        self.driver = driver
        
        
        # 初始化ddddocr
        if DDDDOCR_AVAILABLE:
          try:
                self.alse)
                print("✅ d功")
            except Exception as e:
                pri: {e}")
ne
    
    def detect_slider
        """检测滑块验证码"""
        try:
    ge_source
            
            # 检查验证的检测方法
            if '<divxt:
    lse
          
            print("✅ 检测")
            return True
            
        as e:
            print(f"❌ 滑块检测失败: ")
            return Fa
    
    def handle_captcha_reference_algorit
        """
        
        基于 real_tiktok_scraping_service.cha 方法
        """
        try:
            # 多次检查验证
            for attempt in range(3):
                html_text = self.drisource
                
        
                if '<div id="captcha_
        lse
                
                if attempt == 0:
                    print("🔐 检测到验证码，正在处理...")
        se:
                
                
                # 查找验证码图片 - 使用参考项目的方法
        
                if2:
                    print("⚠️ 验证码图片")
                    con
         
                try:
                    # 获取验证码图片URL
            )
                
                    
                    print(f"背景图URL: {background_img_ur
                    print(f"滑块图URL: {target_i
                    
                    # 下载验片
                
                    target_response = reques0)
                    
                    if backgr:
                        # 使用ddddocr的滑块匹配功能 - 参考项目的核心算法
                        background_byteontent
                        target_bytnt
                        
                     
                        try:
                    
                            if res s:
                                target_x = res[
                                print(f")
                                
                        法
                                x_']
                               
                                # 获取图片尺寸进行缩放 - 参考项目的精确算法
                                img_array = np.fro.uint8)
                                imOLOR)
                         one:
                     shape[:2]
                                    # 按比例- 关键算法
                            ffset
        }")
                
                   t}")
                                 x}")
            :
                et
                                    print(f"📐
                                
                
                                success = self_x)
                                if success:
                否通过
                               
                                    new_html = self.driver.page_source
                                    if "captcha
                    )
                                    
                        e:
                                     试")
                                else:
                                    
                            else:
                             ")
                                
                        exc
                            e}")
                        案
                     
                            print(f"🎲 使用随机滑动距离")
                    tance)
                            if sucss:
                                time.sleep(3)
                    
             待一段时间再重试
                    if attempt < 2:
                        tim2)
                        self.drive.refresh()
                        time.sleep(2)
                        
        s e:
                    pr")
        
            
            # 所有尝试都失败了
            print("❌)
    
            
        exceion as e:
            print(f"❌ 滑块处理异常
            return True
    
    def perform_slide_reference_method(self, distance: flo
        """
        使用参考
        基于Selenium的Action的drag操作
        """
        try:
            # 查找滑块元素 - 使用参考项目的精确选择器
ne
            
            #
            slider_selector [
                "xpath://*,
                ".secsdk-captcha-drag-icon",
    
            ]
    
            for:
                try:
                    if sele"):
                        # 处理xpath选择器
                        xpath = se
                        slider_element h)
                    else:
                        slide)
        
                    if slider_element and ayed():
         r}")
                        bk
                except:
tinue
            
            main()
  main__":__ == "e__

if __nam实现")一步调试算法需要进  print("      ！")
"\n❌ 测试失败t(        prinse:
")
    el目算法实现正常工作t("参考项 prin    ")
   \n🎉 测试成功！  print("
      if success:
    
    d_slider()ancetest_enhcess =   suc
    
  机制和异常处理") 多次重试print("- ✅")
    的drag操作方法✅ 模拟参考项目"-    print(
 离")缩放计算实际滑动距✅ 按比例- rint("
    p")行精确位置识别✅ 使用ddddocr进nt("-   pri")
  n🔧 算法特点:"\nt(")
    pri参数算法和关键于成功项目的核心("基print法实现")
    滑块处理 - 参考项目算t("TikTok
    prin"""""主函数:
    "in()def ma关闭")

可能已经erDriv⚠️  Web("     print       
  except:    r已关闭")
  ve WebDrit("✅    prin()
        r.quit   drive:
         
        tryinally:
    false
    eturn F           r
 : {e}") 测试过程中发生错误  print(f"❌
           else:      ue
 return Tr          e}")
  异常，验证成功: {面跳转🎊 检测到页rint(f"        pr(e):
    ed" in stclosow already arget wind"t or in str(e)ow" uch wind if "no s的异常
       跳转导致 检查是否是因为页面      #
   e:ption asExce except            
rn True
        retu")
"\nrint(     p
          eep(1)
 .slme    ti    ue)
    ush=Tr, fl""秒", end=间: {i}t(f"\r剩余时in  pr     ):
     , -1(30, 0range in r i
        fo)察..."持打开30秒供观"\n🔍 浏览器将保print(f    打开观察
        # 保持浏览器
            turn False
     re")
       滑块处理失败 print("❌ 
           lse: e       e
eturn Tru    r           
 ")断，验证可能成功据异常判"🎊 根print(              {e}")
  面跳转）: 终状态（可能是页无法获取最"⚠️  rint(f    p         e:
   ion as Except    except              
          rue
       return T                  块处理报告成功")
  页面未跳转，但滑int("⚠️       pr        
        else:            rue
    return T            
     面已跳转到搜索结果")功！页"🎊 验证成t(in      pr            _title:
   finalnot inity Check" curl or "Search_ur_url != seif final        
                    ")
    e}al_titl 最终标题: {fin print(f"✅               l_url}")
RL: {finaf"✅ 最终Urint(          p          
        itle
    driver.t_title =   final         l
     urnt_redriver.cur_url =        final      
        try:       # 检查最终状态
         
              ！")
 ("🎉 滑块处理成功  print     tcha:
     _capf not has  i   
          ")
 :.2f} 秒- start_timend_time {et(f"处理耗时:   prin     
   ()
      = time.time  end_time      ithm()
 orrence_algefeha_rle_captc.handder_handlerliaptcha = shas_c  
      
        () time.timetart_time =    s
    ...")考项目的成功算法用参t("\n🎯 开始使  prin
      考项目的算法处理滑块用参        # 使
        
r)er(drivedSliderHandlanceer = Enhlider_handl      s  强滑块处理器
  # 创建增 
      ")
       ...使用参考项目算法处理检测到滑块验证页面，nt("🔍         pri  
rue
      urn T     ret  
     ，直接访问成功") 无需滑块验证 print("✅           le:
 driver.titck" not inCheecurity   if "S   
   是否需要滑块验证   # 检查     
     )
   "er.title}: {driv✅ 页面标题nt(f"       pri")
 rrent_url} {driver.cu当前URL:"✅ (f print
               ep(5)
ime.sle t    
   earch_url)ver.get(s dri            
 
  )l}"arch_urse问页面: {int(f"🔄 访     prcase"
   e%20/phonm/shop/stok.coww.tik//w"https:= url h_rcea   s    hop
 问TikTok S
        # 访  try:e
    
  Falseturn 
        r not driver:
    ifbdriver()eate_wedriver = cr    )
    
60"=" * t(
    prin测试")块处理项目算法的增强滑"🚀 基于参考
    print("试增强版滑块处理"""""测
    :r()ced_slideenhanst_e

def teturn Non   ree}")
     失败: {er创建f"WebDrivnt(     prin as e:
   tioxceppt Ece    exr
urn drive    ret 
           ut(30)
eoage_load_timver.set_p        driined})")
() => undeft: er', {gedrivweb, '(navigatornePropertyject.defiscript("Obver.execute_dris)
        ontie_ops=chromice, optionservrvice=rome(seriver.Cher = webd        driv)
l().instalrManager()ivee(ChromeDr = Servicervice     s   
   
      False)xtension',omationEn('useAutental_optiodd_experimns.arome_optio   ch
     ation"])ble-autom"enaitches", [xcludeSwoption("eimental_experdd_s.arome_option      ch
  lled')mationControtures=Autonk-feabli--disable-ent('_argumions.addome_opt   chr)
     shm-usage'ev-e-dnt('--disabladd_argumeoptions.  chrome_      )
sandbox'o-ment('--ns.add_argue_optionhrom
        cns()ons = Optio chrome_opti  
     "
    try:ver"""创建WebDri ""
   ver():reate_webdrif c

den Falseetur  r         : {e}")
 失败"❌ 滑动操作(f    print       as e:
  xception  except E        
    rue
          return T       ")
 "✅ 滑动操作执行完成   print(
                    orm()
 perf    actions.      ease()
  rel actions.           释放鼠标
   #  
                    .1f} 像素")
e:ncep_distas}: 移动 {step步骤 {i+1}/{stt(f"in    pr            elay)
ep_dp(stslee     time.           )
ete, y_offsep_distancset(stve_by_offmoons.       acti  )
       nt(-2, 2ndom.randie ra i == 0 elsfset = 10 if y_of            参数
   模拟参考项目的y=10垂直偏移，    # 添加          s):
  tepange(sfor i in r               
   
      ps}步执行") 分{stestance:.1f},{di始滑动: 总距离="🎯 开t(f      prin       
         ps
  te = 0.2 / s_delay        steps
    ce / stepe = distanancdisttep_         s  
  = 10ps     ste     秒
  骤，持续0.2个小步     # 分解为多)
       0, 0.2tual_x, 1参考项目的drag(ac- 模拟 # 执行滑动             
     .3))
      1, 0niform(0.m.usleep(randome.       ti操作
     始延迟，模拟人工# 添加初            
           element)
 ider__hold(slns.click_and   actio         
击并按住滑块   # 点             
 
       driver)hains(self.nCons = Actio  acti    
               ins操作
   ctionCha的Alenium转换为Se        # 2)
    0., 10, _xrag(actual.delementr_参考项目: slide     #       的drag操作
 考项目# 模拟参           
            se
 rn Fal    retu           ")
 元素滑块("❌ 未找到  print            ement:
  ider_elf not sl  i