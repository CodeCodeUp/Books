import pymysql
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import Config
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """数据加载器 - 启动时全量加载，后续增量更新"""
    
    def __init__(self):
        self.db_config = Config.DB_CONFIG
        # 创建SQLAlchemy引擎
        self.engine = create_engine(
            f"mysql+pymysql://{self.db_config['user']}:{self.db_config['password']}@"
            f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}?"
            f"charset={self.db_config['charset']}"
        )
        
        # 缓存数据和最后更新时间
        self._ratings_df = None
        self._books_df = None
        self._last_ratings_update = None
        self._last_books_update = None
        
    def initialize_data(self):
        """初始化时全量加载数据"""
        logger.info("=== 启动时全量加载数据 ===")
        
        self._ratings_df = self._load_ratings_full()
        self._books_df = self._load_books_full()
        
        # 记录加载时间
        self._last_ratings_update = datetime.now()
        self._last_books_update = datetime.now()
        
        logger.info("数据初始化完成")
        
    def _load_ratings_full(self):
        """全量加载评分数据"""
        logger.info("全量加载评分数据...")
        
        query = """
        SELECT user_id, book_id, rating, created_at
        FROM ratings 
        WHERE rating > 0
        ORDER BY created_at DESC
        """
        
        ratings_df = pd.read_sql(query, self.engine)
        logger.info(f"加载评分数据: {len(ratings_df):,} 条")
        
        return ratings_df
    
    def _load_books_full(self):
        """全量加载图书数据"""
        logger.info("全量加载图书数据...")
        
        query = """
        SELECT book_id, title, author, publisher, year, 
               avg_rating, rating_count, created_at,
               image_url_s, image_url_m, image_url_l
        FROM books 
        WHERE rating_count > 0
        ORDER BY created_at DESC
        """
        
        books_df = pd.read_sql(query, self.engine)
        logger.info(f"加载图书数据: {len(books_df):,} 条")
        
        return books_df
    
    def get_ratings_data(self, force_refresh=False):
        """
        获取评分数据（增量更新）

        参数:
            force_refresh: 强制检查增量更新（而非全量加载）
        """
        # 首次调用，全量加载
        if self._ratings_df is None:
            self.initialize_data()
            return self._ratings_df

        # force_refresh=True 时，强制检查增量更新（不是重新全量加载）
        # 检查是否有新评分
        try:
            new_ratings_query = """
            SELECT user_id, book_id, rating, created_at
            FROM ratings
            WHERE created_at > %(last_update)s AND rating > 0
            ORDER BY created_at DESC
            """

            new_ratings = pd.read_sql(
                new_ratings_query,
                self.engine,
                params={'last_update': self._last_ratings_update}
            )

            if not new_ratings.empty:
                logger.info(f"发现 {len(new_ratings)} 条新评分，增量更新数据...")

                # 合并新数据
                self._ratings_df = pd.concat([new_ratings, self._ratings_df], ignore_index=True)

                # 去重（同一用户对同一图书的最新评分）
                self._ratings_df = self._ratings_df.sort_values('created_at', ascending=False)
                self._ratings_df = self._ratings_df.drop_duplicates(
                    subset=['user_id', 'book_id'],
                    keep='first'
                )

                self._last_ratings_update = datetime.now()
                logger.info(f"评分数据增量更新完成，当前总数: {len(self._ratings_df):,}")
            else:
                if force_refresh:
                    logger.info("未发现新评分，使用缓存数据")

            return self._ratings_df

        except Exception as e:
            logger.error(f"增量更新评分数据失败: {e}")
            return self._ratings_df
    
    def get_books_data(self, force_refresh=False):
        """
        获取图书数据（增量更新）

        参数:
            force_refresh: 强制检查增量更新（而非全量加载）
        """
        # 首次调用，全量加载
        if self._books_df is None:
            self.initialize_data()
            return self._books_df

        # force_refresh=True 时，强制检查增量更新
        # 注意：这里不是全量加载，而是立即检查是否有更新
        
        # 检查是否有图书统计更新
        try:
            updated_books_query = """
            SELECT book_id, title, author, publisher, year, 
                   avg_rating, rating_count, created_at,
                   image_url_s, image_url_m, image_url_l
            FROM books 
            WHERE created_at > %(last_update)s AND rating_count > 0
            ORDER BY created_at DESC
            """
            
            updated_books = pd.read_sql(
                updated_books_query,
                self.engine,
                params={'last_update': self._last_books_update}
            )
            
            if not updated_books.empty:
                logger.info(f"发现 {len(updated_books)} 本图书统计更新...")
                
                # 更新现有数据
                for _, updated_book in updated_books.iterrows():
                    book_id = updated_book['book_id']
                    mask = self._books_df['book_id'] == book_id
                    
                    if mask.any():
                        # 更新现有图书信息
                        self._books_df.loc[mask] = updated_book
                    else:
                        # 添加新图书
                        self._books_df = pd.concat([self._books_df, updated_book.to_frame().T], ignore_index=True)
                
                self._last_books_update = datetime.now()
                logger.info("图书数据更新完成")
            
            return self._books_df
            
        except Exception as e:
            logger.error(f"增量更新图书数据失败: {e}")
            return self._books_df
    
    # 保持向后兼容的接口
    def load_ratings_data(self):
        """向后兼容接口"""
        return self.get_ratings_data()
    
    def load_book_data(self):
        """向后兼容接口"""
        return self.get_books_data()
    
    def get_user_rated_books(self, user_id):
        """获取用户已评分的图书"""
        try:
            query = """
            SELECT r.book_id, r.rating, b.title, b.author
            FROM ratings r
            JOIN books b ON r.book_id = b.book_id
            WHERE r.user_id = %(user_id)s
            ORDER BY r.rating_date DESC
            """

            user_ratings = pd.read_sql(query, self.engine, params={'user_id': user_id})

            return user_ratings

        except Exception as e:
            logger.error(f"获取用户已评分图书失败: {e}")
            return pd.DataFrame()

    def get_user_interests(self, user_id):
        """
        获取用户兴趣主题ID列表

        参数:
            user_id: 用户ID

        返回:
            list[int]: 用户选择的兴趣主题ID列表
        """
        try:
            query = """
            SELECT theme_id
            FROM user_interests
            WHERE user_id = %(user_id)s
            """

            result = pd.read_sql(query, self.engine, params={'user_id': user_id})

            if result.empty:
                return []

            return result['theme_id'].tolist()

        except Exception as e:
            logger.error(f"获取用户兴趣失败: {e}")
            return []

    def get_books_by_themes(self, theme_ids, exclude_book_ids=None, limit=100):
        """
        根据主题ID列表获取相关图书

        参数:
            theme_ids: 主题ID列表
            exclude_book_ids: 需要排除的图书ID集合
            limit: 返回数量限制

        返回:
            DataFrame: 符合主题的图书列表
        """
        if not theme_ids:
            return pd.DataFrame()

        try:
            # 构建 IN 子句的占位符
            placeholders = ', '.join(['%s'] * len(theme_ids))

            query = f"""
            SELECT book_id, title, author, publisher, year,
                   avg_rating, rating_count, theme_id,
                   image_url_s, image_url_m, image_url_l
            FROM books
            WHERE theme_id IN ({placeholders})
              AND rating_count >= 5
              AND avg_rating >= 3.0
            ORDER BY avg_rating DESC, rating_count DESC
            LIMIT {limit * 2}
            """

            # params 必须是元组格式
            result = pd.read_sql(query, self.engine, params=tuple(theme_ids))

            # 排除指定图书
            if exclude_book_ids and not result.empty:
                result = result[~result['book_id'].isin(exclude_book_ids)]

            return result.head(limit)

        except Exception as e:
            logger.error(f"根据主题获取图书失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()