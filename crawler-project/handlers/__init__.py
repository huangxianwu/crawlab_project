# 处理器包
# 包含各种功能处理器：滑块处理、数据提取等

# 🔧 关键修复：在任何导入之前就修复路径
import sys
import os

# 获取项目根目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 确保项目根目录在Python路径的最前面
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 额外保险：也确保当前目录在路径中
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 🔍 增强调试信息 - 始终显示以便Crawlab调试
print("🔍 [DEBUG] handlers/__init__.py 路径调试信息")
print(f"[DEBUG] 当前文件: {__file__}")
print(f"[DEBUG] current_dir: {current_dir}")
print(f"[DEBUG] project_root: {project_root}")
print(f"[DEBUG] 工作目录: {os.getcwd()}")
print(f"[DEBUG] sys.path前5个:")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

# 检查关键文件是否存在
key_files = ['utils/__init__.py', 'utils/logger.py', 'config.py']
for file_path in key_files:
    full_path = os.path.join(project_root, file_path)
    exists = os.path.exists(full_path)
    print(f"[DEBUG] {file_path}: 存在={exists} ({full_path})")

# 尝试直接导入测试
print(f"[DEBUG] handlers/__init__.py 导入测试:")
try:
    import utils
    print(f"  ✅ import utils 成功")
except Exception as e:
    print(f"  ❌ import utils 失败: {e}")

try:
    from utils.logger import get_logger
    print(f"  ✅ from utils.logger import get_logger 成功")
except Exception as e:
    print(f"  ❌ from utils.logger import get_logger 失败: {e}")

print("-" * 40)

# 现在安全地导入模块
from .slider import SliderHandler
from .extractor import DataExtractor

__all__ = ['SliderHandler', 'DataExtractor']