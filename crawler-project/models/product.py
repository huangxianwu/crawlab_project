"""
商品数据模型
简化版本，仅包含核心字段：关键词、标题、采集时间
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProductData:
    """商品数据模型 - MVP简化版本"""
    keyword: str
    title: str
    scraped_at: datetime
    slider_encountered: bool = False
    slider_solved: bool = False
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于MongoDB存储"""
        return {
            "keyword": self.keyword,
            "title": self.title,
            "scraped_at": self.scraped_at.isoformat(),
            "slider_encountered": self.slider_encountered,
            "slider_solved": self.slider_solved
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProductData':
        """从字典创建ProductData对象"""
        return cls(
            keyword=data["keyword"],
            title=data["title"],
            scraped_at=datetime.fromisoformat(data["scraped_at"]),
            slider_encountered=data.get("slider_encountered", False),
            slider_solved=data.get("slider_solved", False)
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ProductData(keyword='{self.keyword}', title='{self.title}')"