#!/usr/bin/env python3
"""
Crawlab部署脚本
将爬虫项目部署到Crawlab平台
"""
import os
import sys
import json
import shutil
import zipfile
from pathlib import Path


def create_crawlab_package():
    """创建Crawlab爬虫包"""
    print("🚀 创建Crawlab爬虫包...")
    
    # 创建临时目录
    package_dir = Path("crawlab_package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 需要包含的文件和目录
    include_files = [
        "crawlab_spider.py",
        "spider.json",
        "requirements.txt",
        "config.py",
        "models/",
        "utils/",
        "handlers/",
        "README.md"
    ]
    
    # 复制文件到包目录
    for item in include_files:
        src_path = Path(item)
        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, package_dir / src_path.name)
                print(f"✅ 复制文件: {item}")
            elif src_path.is_dir():
                shutil.copytree(src_path, package_dir / src_path.name)
                print(f"✅ 复制目录: {item}")
        else:
            print(f"⚠️ 文件不存在: {item}")
    
    # 创建ZIP包
    zip_path = Path("ecommerce_crawler.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_path)
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    
    print(f"✅ Crawlab爬虫包创建完成: {zip_path}")
    return zip_path


def validate_spider_config():
    """验证爬虫配置"""
    print("\n🔍 验证爬虫配置...")
    
    # 检查spider.json
    spider_json_path = Path("spider.json")
    if not spider_json_path.exists():
        print("❌ spider.json文件不存在")
        return False
    
    try:
        with open(spider_json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证必要字段
        required_fields = ['name', 'cmd', 'params']
        for field in required_fields:
            if field not in config:
                print(f"❌ spider.json缺少必要字段: {field}")
                return False
        
        print("✅ spider.json配置验证通过")
        
        # 显示配置信息
        print(f"  爬虫名称: {config['name']}")
        print(f"  执行命令: {config['cmd']}")
        print(f"  参数数量: {len(config.get('params', []))}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ spider.json格式错误: {e}")
        return False


def test_spider_locally():
    """本地测试爬虫"""
    print("\n🧪 本地测试爬虫...")
    
    try:
        # 测试导入
        sys.path.append('.')
        
        print("测试模块导入...")
        from config import Config
        from utils.logger import setup_logger
        from models.product import ProductData
        print("✅ 核心模块导入成功")
        
        # 测试爬虫脚本语法
        print("测试爬虫脚本语法...")
        with open('crawlab_spider.py', 'r', encoding='utf-8') as f:
            spider_code = f.read()
        
        compile(spider_code, 'crawlab_spider.py', 'exec')
        print("✅ 爬虫脚本语法检查通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 本地测试失败: {e}")
        return False


def generate_deployment_guide():
    """生成部署指南"""
    print("\n📝 生成部署指南...")
    
    guide_content = """# Crawlab电商爬虫部署指南

## 1. 准备工作

### 1.1 确保Crawlab环境运行正常
```bash
# 检查Crawlab服务状态
docker-compose ps

# 访问Crawlab Web界面
# http://localhost:8080
```

### 1.2 准备爬虫包
- 爬虫包文件: `ecommerce_crawler.zip`
- 包含所有必要的代码和配置文件

## 2. 部署步骤

### 2.1 上传爬虫
1. 登录Crawlab Web界面 (http://localhost:8080)
2. 进入"爬虫"页面
3. 点击"新建爬虫"
4. 选择"上传ZIP文件"
5. 上传 `ecommerce_crawler.zip`
6. 等待上传和解析完成

### 2.2 配置爬虫
1. 爬虫名称: "电商爬虫"
2. 执行命令: `python crawlab_spider.py`
3. 配置参数:
   - keywords: 搜索关键词 (默认: phone case,wireless charger)
   - max_pages: 最大页数 (默认: 1)

### 2.3 环境变量配置
- MONGO_URI: mongodb://mongo:27017
- DATABASE_NAME: crawler_db
- LOG_LEVEL: INFO

## 3. 运行测试

### 3.1 创建任务
1. 进入爬虫详情页
2. 点击"运行"按钮
3. 设置参数:
   - keywords: "数据线"
   - max_pages: 1
4. 点击"开始"

### 3.2 监控执行
1. 在"任务"页面查看任务状态
2. 状态变化: 等待中 → 运行中 → 成功
3. 点击任务详情查看日志

### 3.3 查看结果
1. 在任务详情页查看采集统计
2. 在"结果"页面查看采集的商品数据
3. 检查MongoDB数据库中的数据

## 4. 验证标准

- ✅ 在Crawlab Web界面能看到"电商爬虫"项目
- ✅ 能够成功创建和运行任务
- ✅ 任务状态正常变化: 等待中→运行中→成功
- ✅ 能看到完整的执行日志和采集结果统计
- ✅ 数据正确保存到MongoDB数据库

## 5. 故障排除

### 5.1 常见问题
- 依赖安装失败: 检查requirements.txt
- WebDriver错误: 确保Chrome已安装
- 数据库连接失败: 检查MongoDB服务状态
- 滑块处理失败: 检查ddddocr依赖

### 5.2 日志查看
```bash
# 查看Crawlab容器日志
docker-compose logs -f master
docker-compose logs -f worker

# 查看爬虫执行日志
# 在Crawlab Web界面的任务详情页查看
```

## 6. 性能优化

### 6.1 资源配置
- 内存: 建议至少1GB
- CPU: 建议至少2核
- 磁盘: 建议至少500MB

### 6.2 并发配置
- 单节点建议最多2个并发任务
- 可通过增加Worker节点提高并发能力

## 7. 监控和维护

### 7.1 定期检查
- 每日检查任务执行情况
- 监控数据库存储空间
- 检查日志文件大小

### 7.2 数据备份
```bash
# 备份MongoDB数据
docker exec crawlab_mongo mongodump --out /backup/$(date +%Y%m%d)
```
"""
    
    with open('CRAWLAB_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ 部署指南已生成: CRAWLAB_DEPLOYMENT_GUIDE.md")


def main():
    """主函数"""
    print("🚀 Crawlab电商爬虫部署工具")
    print("=" * 50)
    
    # 验证配置
    if not validate_spider_config():
        print("❌ 配置验证失败，请检查spider.json")
        return False
    
    # 本地测试
    if not test_spider_locally():
        print("❌ 本地测试失败，请检查代码")
        return False
    
    # 创建部署包
    zip_path = create_crawlab_package()
    
    # 生成部署指南
    generate_deployment_guide()
    
    print("\n" + "=" * 50)
    print("🎉 Crawlab爬虫部署准备完成！")
    print("=" * 50)
    print(f"📦 爬虫包: {zip_path}")
    print(f"📝 部署指南: CRAWLAB_DEPLOYMENT_GUIDE.md")
    print("\n📋 下一步:")
    print("1. 确保Crawlab服务正在运行")
    print("2. 访问 http://localhost:8080")
    print("3. 上传爬虫包并配置参数")
    print("4. 运行测试任务验证功能")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)