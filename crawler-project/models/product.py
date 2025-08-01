"""
商品数据模型
基于参考项目的完整字段定义
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProductData:
    """商品数据模型 - 基于参考项目的完整版本"""
    # 基本信息
    product_id: str
    title: str
    search_keyword: str
    
    # 价格信息
    current_price: float
    origin_price: float
    shipping_fee: float = 0.0
    
    # 商品信息
    product_image: str = ""
    categories: str = ""
    desc_detail: str = ""
    
    # 销售信息
    sold_count: int = 0
    product_rating: float = 0.0
    review_count: int = 0
    review_count_str: str = "0"
    
    # 评论时间
    latest_review_fmt: str = ""
    earliest_review_fmt: str = ""
    
    # 店铺信息
    shop_name: str = ""
    
    # 采集信息
    create_time: str = ""
    scraped_at: Optional[datetime] = None
    slider_encountered: bool = False
    slider_solved: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
        if not self.create_time:
            self.create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于MongoDB存储"""
        return {
            # 基本信息
            "product_id": self.product_id,
            "title": self.title,
            "search_keyword": self.search_keyword,
            
            # 价格信息
            "current_price": self.current_price,
            "origin_price": self.origin_price,
            "shipping_fee": self.shipping_fee,
            
            # 商品信息
            "product_image": self.product_image,
            "categories": self.categories,
            "desc_detail": self.desc_detail,
            
            # 销售信息
            "sold_count": self.sold_count,
            "product_rating": self.product_rating,
            "review_count": self.review_count,
            "review_count_str": self.review_count_str,
            
            # 评论时间
            "latest_review_fmt": self.latest_review_fmt,
            "earliest_review_fmt": self.earliest_review_fmt,
            
            # 店铺信息
            "shop_name": self.shop_name,
            
            # 采集信息
            "create_time": self.create_time,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else "",
            "slider_encountered": self.slider_encountered,
            "slider_solved": self.slider_solved
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProductData':
        """从字典创建ProductData对象"""
        scraped_at = None
        if data.get("scraped_at"):
            try:
                scraped_at = datetime.fromisoformat(data["scraped_at"])
            except:
                scraped_at = datetime.now()
        
        return cls(
            # 基本信息
            product_id=data.get("product_id", ""),
            title=data.get("title", ""),
            search_keyword=data.get("search_keyword", ""),
            
            # 价格信息
            current_price=float(data.get("current_price", 0.0)),
            origin_price=float(data.get("origin_price", 0.0)),
            shipping_fee=float(data.get("shipping_fee", 0.0)),
            
            # 商品信息
            product_image=data.get("product_image", ""),
            categories=data.get("categories", ""),
            desc_detail=data.get("desc_detail", ""),
            
            # 销售信息
            sold_count=int(data.get("sold_count", 0)),
            product_rating=float(data.get("product_rating", 0.0)),
            review_count=int(data.get("review_count", 0)),
            review_count_str=data.get("review_count_str", "0"),
            
            # 评论时间
            latest_review_fmt=data.get("latest_review_fmt", ""),
            earliest_review_fmt=data.get("earliest_review_fmt", ""),
            
            # 店铺信息
            shop_name=data.get("shop_name", ""),
            
            # 采集信息
            create_time=data.get("create_time", ""),
            scraped_at=scraped_at,
            slider_encountered=data.get("slider_encountered", False),
            slider_solved=data.get("slider_solved", False)
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ProductData(id='{self.product_id}', title='{self.title[:30]}...', price=${self.current_price})"