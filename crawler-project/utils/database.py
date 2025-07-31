"""
MongoDB数据库操作工具
实现基础的CRUD操作
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError

from models.product import ProductData


class DatabaseManager:
    """MongoDB数据库管理器"""
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", 
                 database_name: str = "crawler_db", 
                 collection_name: str = "products"):
        """
        初始化数据库管理器
        
        Args:
            mongo_uri: MongoDB连接URI
            database_name: 数据库名称
            collection_name: 集合名称
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        连接到MongoDB数据库
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # 测试连接
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            self.logger.info(f"成功连接到MongoDB: {self.database_name}.{self.collection_name}")
            return True
            
        except ConnectionFailure as e:
            self.logger.error(f"MongoDB连接失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"数据库初始化异常: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB连接已关闭")
    
    def insert_product(self, product: ProductData) -> bool:
        """
        插入单个商品数据
        
        Args:
            product: 商品数据对象
            
        Returns:
            bool: 插入是否成功
        """
        try:
            if self.collection is None:
                self.logger.error("数据库未连接")
                return False
            
            result = self.collection.insert_one(product.to_dict())
            self.logger.info(f"成功插入商品数据: {product.title}")
            return result.inserted_id is not None
            
        except PyMongoError as e:
            self.logger.error(f"插入商品数据失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"插入数据异常: {e}")
            return False
    
    def insert_products(self, products: List[ProductData]) -> int:
        """
        批量插入商品数据
        
        Args:
            products: 商品数据列表
            
        Returns:
            int: 成功插入的数量
        """
        try:
            if self.collection is None or not products:
                return 0
            
            documents = [product.to_dict() for product in products]
            result = self.collection.insert_many(documents)
            
            inserted_count = len(result.inserted_ids)
            self.logger.info(f"批量插入商品数据成功: {inserted_count}条")
            return inserted_count
            
        except PyMongoError as e:
            self.logger.error(f"批量插入失败: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"批量插入异常: {e}")
            return 0
    
    def find_products_by_keyword(self, keyword: str) -> List[ProductData]:
        """
        根据关键词查询商品数据
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[ProductData]: 商品数据列表
        """
        try:
            if self.collection is None:
                self.logger.error("数据库未连接")
                return []
            
            cursor = self.collection.find({"keyword": keyword})
            products = []
            
            for doc in cursor:
                try:
                    product = ProductData.from_dict(doc)
                    products.append(product)
                except Exception as e:
                    self.logger.warning(f"解析商品数据失败: {e}")
                    continue
            
            self.logger.info(f"查询到关键词'{keyword}'的商品数据: {len(products)}条")
            return products
            
        except PyMongoError as e:
            self.logger.error(f"查询商品数据失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"查询数据异常: {e}")
            return []
    
    def find_all_products(self, limit: int = 100) -> List[ProductData]:
        """
        查询所有商品数据
        
        Args:
            limit: 限制返回数量
            
        Returns:
            List[ProductData]: 商品数据列表
        """
        try:
            if self.collection is None:
                self.logger.error("数据库未连接")
                return []
            
            cursor = self.collection.find().limit(limit)
            products = []
            
            for doc in cursor:
                try:
                    product = ProductData.from_dict(doc)
                    products.append(product)
                except Exception as e:
                    self.logger.warning(f"解析商品数据失败: {e}")
                    continue
            
            self.logger.info(f"查询到商品数据: {len(products)}条")
            return products
            
        except PyMongoError as e:
            self.logger.error(f"查询所有商品数据失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"查询数据异常: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            if self.collection is None:
                return {"error": "数据库未连接"}
            
            total_count = self.collection.count_documents({})
            slider_encountered = self.collection.count_documents({"slider_encountered": True})
            slider_solved = self.collection.count_documents({"slider_solved": True})
            
            # 按关键词统计
            pipeline = [
                {"$group": {"_id": "$keyword", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            keyword_stats = list(self.collection.aggregate(pipeline))
            
            stats = {
                "total_products": total_count,
                "slider_encountered": slider_encountered,
                "slider_solved": slider_solved,
                "slider_success_rate": round(slider_solved / slider_encountered * 100, 2) if slider_encountered > 0 else 0,
                "keyword_stats": keyword_stats[:10]  # 前10个关键词
            }
            
            self.logger.info(f"统计信息: 总计{total_count}条数据")
            return stats
            
        except PyMongoError as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}
        except Exception as e:
            self.logger.error(f"统计信息异常: {e}")
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """
        清空集合数据（测试用）
        
        Returns:
            bool: 清空是否成功
        """
        try:
            if self.collection is None:
                self.logger.error("数据库未连接")
                return False
            
            result = self.collection.delete_many({})
            self.logger.info(f"清空集合成功，删除了{result.deleted_count}条数据")
            return True
            
        except PyMongoError as e:
            self.logger.error(f"清空集合失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"清空集合异常: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager