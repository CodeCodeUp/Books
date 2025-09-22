import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class SimilarityCalculator:
    """相似度计算工具类"""
    
    @staticmethod
    def cosine_similarity_users(rating_matrix, user_id):
        """计算用户之间的余弦相似度"""
        try:
            if user_id not in rating_matrix.index:
                logger.warning(f"用户 {user_id} 不在评分矩阵中")
                return pd.Series()
            
            # 获取目标用户的评分向量
            target_user_ratings = rating_matrix.loc[user_id].values.reshape(1, -1)
            
            # 计算与所有用户的相似度
            similarities = cosine_similarity(target_user_ratings, rating_matrix.values)[0]
            
            # 创建相似度Series
            similarity_series = pd.Series(similarities, index=rating_matrix.index)
            
            # 移除自己
            similarity_series = similarity_series.drop(user_id)
            
            # 只保留有共同评分的用户
            similarity_series = similarity_series[similarity_series > 0]
            
            return similarity_series.sort_values(ascending=False)
            
        except Exception as e:
            logger.error(f"计算用户相似度失败: {e}")
            return pd.Series()
    
    @staticmethod
    def pearson_correlation_users(rating_matrix, user_id):
        """计算用户之间的皮尔逊相关系数"""
        try:
            if user_id not in rating_matrix.index:
                return pd.Series()
            
            target_user = rating_matrix.loc[user_id]
            
            # 计算皮尔逊相关系数
            correlations = rating_matrix.corrwith(target_user)
            
            # 移除自己和NaN值
            correlations = correlations.drop(user_id)
            correlations = correlations.dropna()
            
            return correlations.sort_values(ascending=False)
            
        except Exception as e:
            logger.error(f"计算皮尔逊相关系数失败: {e}")
            return pd.Series()
    
    @staticmethod
    def jaccard_similarity_users(rating_matrix, user_id):
        """计算用户之间的Jaccard相似度（基于共同评分的图书）"""
        try:
            if user_id not in rating_matrix.index:
                return pd.Series()
            
            target_user = rating_matrix.loc[user_id]
            target_rated_books = set(target_user[target_user > 0].index)
            
            similarities = {}
            
            for other_user in rating_matrix.index:
                if other_user == user_id:
                    continue
                    
                other_rated_books = set(rating_matrix.loc[other_user][rating_matrix.loc[other_user] > 0].index)
                
                # 计算Jaccard相似度
                intersection = len(target_rated_books & other_rated_books)
                union = len(target_rated_books | other_rated_books)
                
                if union > 0:
                    similarities[other_user] = intersection / union
            
            return pd.Series(similarities).sort_values(ascending=False)
            
        except Exception as e:
            logger.error(f"计算Jaccard相似度失败: {e}")
            return pd.Series()
    
    @staticmethod
    def find_common_rated_items(rating_matrix, user1, user2):
        """找到两个用户共同评分的物品"""
        try:
            user1_ratings = rating_matrix.loc[user1]
            user2_ratings = rating_matrix.loc[user2]
            
            # 找到两个用户都评分过的图书
            common_items = rating_matrix.columns[
                (user1_ratings > 0) & (user2_ratings > 0)
            ]
            
            return common_items
            
        except Exception as e:
            logger.error(f"查找共同评分物品失败: {e}")
            return []