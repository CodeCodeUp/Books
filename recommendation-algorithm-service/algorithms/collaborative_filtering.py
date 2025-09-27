import numpy as np
import pandas as pd
import logging
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from data.data_loader import DataLoader
from utils.cache import RecommendationCache
from config import Config

logger = logging.getLogger(__name__)

class UserBasedCollaborativeFiltering:
    """基于用户的协同过滤推荐算法 - 内存优化版本"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.cache = RecommendationCache()
        self.data_initialized = False
        
    def load_data(self):
        """加载数据（启动时初始化，后续增量更新）"""
        if not self.data_initialized:
            logger.info("=== 首次数据加载和初始化 ===")
            self.data_loader.initialize_data()
            self.data_initialized = True
        else:
            logger.info("=== 增量数据更新 ===")
        
        # 获取最新数据（自动处理增量更新）
        self.ratings_df = self.data_loader.get_ratings_data()
        self.books_df = self.data_loader.get_books_data()
        
        logger.info("数据加载/更新完成")
        
    def find_similar_users_efficient(self, target_user_id, min_common_items=2, top_k=50):
        """高效查找相似用户（降低共同评分要求）"""
        logger.info(f"为用户 {target_user_id} 查找相似用户...")
        
        try:
            # 获取目标用户的评分记录
            target_user_ratings = self.ratings_df[
                self.ratings_df['user_id'] == target_user_id
            ]
            
            if target_user_ratings.empty:
                logger.warning(f"用户 {target_user_id} 没有评分记录")
                return []
            
            target_books = set(target_user_ratings['book_id'].values)
            target_ratings_dict = dict(zip(
                target_user_ratings['book_id'], 
                target_user_ratings['rating']
            ))
            
            logger.info(f"目标用户评分了 {len(target_books)} 本图书")
            
            # 找到与目标用户有共同评分图书的用户
            common_users_df = self.ratings_df[
                self.ratings_df['book_id'].isin(target_books) & 
                (self.ratings_df['user_id'] != target_user_id)
            ]
            
            # 按用户分组，计算共同评分图书数量
            common_counts = common_users_df.groupby('user_id')['book_id'].count()
            qualified_users = common_counts[common_counts >= min_common_items].index
            
            logger.info(f"找到 {len(qualified_users)} 个有共同评分的用户（最少{min_common_items}本共同图书）")
            
            # 计算相似度
            similarities = []
            
            for other_user_id in qualified_users:
                if len(similarities) >= top_k * 3:  # 计算更多候选
                    break
                    
                similarity = self._calculate_user_similarity_fast(
                    target_user_id, other_user_id, target_ratings_dict
                )
                
                if similarity > 0.6:  # 降低相似度阈值
                    similarities.append({
                        'user_id': other_user_id,
                        'similarity': similarity
                    })
            
            # 按相似度排序
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"计算得到 {len(similarities)} 个相似用户")
            
            # 调试：显示前5个相似用户
            for i, sim_user in enumerate(similarities[:5]):
                logger.info(f"  相似用户 {i+1}: ID={sim_user['user_id']}, 相似度={sim_user['similarity']:.3f}")
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"查找相似用户失败: {e}")
            return []
    
    def _calculate_user_similarity_fast(self, user1_id, user2_id, user1_ratings_dict):
        """快速计算两个用户的相似度"""
        try:
            # 获取用户2的评分
            user2_ratings = self.ratings_df[
                self.ratings_df['user_id'] == user2_id
            ]
            user2_ratings_dict = dict(zip(user2_ratings['book_id'], user2_ratings['rating']))
            
            # 找到共同评分的图书
            common_books = set(user1_ratings_dict.keys()) & set(user2_ratings_dict.keys())
            
            if len(common_books) < 2:  # 降低到至少2本共同图书
                return 0.0
            
            # 调试输出
            logger.debug(f"用户 {user1_id} 和用户 {user2_id} 有 {len(common_books)} 本共同评分图书")
            
            # 计算余弦相似度
            user1_vector = [user1_ratings_dict[book] for book in common_books]
            user2_vector = [user2_ratings_dict[book] for book in common_books]
            
            user1_array = np.array(user1_vector).reshape(1, -1)
            user2_array = np.array(user2_vector).reshape(1, -1)
            
            similarity = cosine_similarity(user1_array, user2_array)[0][0]
            
            # 调试输出
            if similarity > 0.1:
                logger.info(f"  用户 {user1_id} 和 {user2_id} 相似度: {similarity:.3f} (共同图书: {len(common_books)})")
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"计算用户相似度失败: {e}")
            return 0.0
    
    def get_recommendations(self, user_id, top_n=None, min_rating=3.0):
        """为用户生成推荐（优化版本）"""
        if top_n is None:
            top_n = Config.DEFAULT_TOP_N
            
        logger.info(f"=== 为用户 {user_id} 生成推荐 ===")
        
        # 检查缓存
        cached_recommendations = self.cache.load_recommendations(user_id)
        if cached_recommendations:
            logger.info(f"从缓存返回用户 {user_id} 的推荐结果")
            return cached_recommendations[:top_n]
        
        try:
            # 确保数据已加载
            if self.ratings_df is None:
                self.load_data()
            
            # 检查用户是否有评分记录
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
            if user_ratings.empty:
                logger.warning(f"用户 {user_id} 没有评分记录")
                return []  # 不做降级，返回空结果让混合推荐处理
            
            # 高效查找相似用户
            similar_users = self.find_similar_users_efficient(user_id)
            
            if not similar_users:
                logger.warning(f"用户 {user_id} 没有找到相似用户")
                return []  # 不做降级，返回空结果让混合推荐处理
            
            # 生成推荐
            recommendations = self._generate_recommendations_efficient(
                user_id, similar_users, top_n, min_rating
            )
            
            # 缓存结果
            if recommendations:
                self.cache.save_recommendations(user_id, recommendations, 'user_based_cf')
            
            logger.info(f"成功生成 {len(recommendations)} 个推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"生成推荐失败: {e}")
            return []  # 不做降级，返回空结果
    
    def _generate_recommendations_efficient(self, user_id, similar_users, top_n, min_rating):
        """高效生成推荐"""
        logger.info(f"基于 {len(similar_users)} 个相似用户生成推荐")
        
        # 获取用户已评分的图书
        user_rated_books = set(
            self.ratings_df[self.ratings_df['user_id'] == user_id]['book_id'].values
        )
        
        # 收集候选图书（从相似用户的高分图书中）
        candidate_books = {}
        
        for similar_user in similar_users[:20]:  # 只使用前20个最相似用户
            user_id_similar = similar_user['user_id']
            similarity_score = similar_user['similarity']
            
            # 获取该相似用户的高分图书
            similar_user_books = self.ratings_df[
                (self.ratings_df['user_id'] == user_id_similar) & 
                (self.ratings_df['rating'] >= min_rating)
            ]
            
            for _, row in similar_user_books.iterrows():
                book_id = row['book_id']
                rating = row['rating']
                
                if book_id not in user_rated_books:
                    if book_id not in candidate_books:
                        candidate_books[book_id] = []
                    
                    candidate_books[book_id].append({
                        'rating': rating,
                        'similarity': similarity_score
                    })
        
        # 计算每本书的预测评分
        predictions = []
        
        for book_id, ratings_data in candidate_books.items():
            if len(ratings_data) >= 2:  # 至少2个相似用户评分过
                # 加权平均计算预测评分
                weighted_sum = sum(r['rating'] * r['similarity'] for r in ratings_data)
                similarity_sum = sum(r['similarity'] for r in ratings_data)
                
                predicted_rating = weighted_sum / similarity_sum if similarity_sum > 0 else 0
                
                if predicted_rating >= min_rating:
                    predictions.append({
                        'book_id': book_id,
                        'predicted_rating': predicted_rating,
                        'support_users': len(ratings_data)
                    })
        
        # 按预测评分排序
        predictions.sort(key=lambda x: (x['predicted_rating'], x['support_users']), reverse=True)
        
        # 获取top_n推荐并补充图书信息
        top_predictions = predictions[:top_n]
        
        return self._enrich_recommendations(top_predictions, len(similar_users))
    
    def _enrich_recommendations(self, predictions, similar_user_count):
        """补充推荐结果的图书信息"""
        recommendations = []
        
        for pred in predictions:
            book_info = self.books_df[
                self.books_df['book_id'] == pred['book_id']
            ]
            
            if not book_info.empty:
                book_data = book_info.iloc[0]
                recommendations.append({
                    'bookId': pred['book_id'],  # 统一字段名
                    'title': book_data['title'],
                    'author': book_data['author'] or '未知作者',
                    'publisher': book_data.get('publisher', '') or '',
                    'year': int(book_data['year']) if pd.notna(book_data['year']) else None,
                    'imageUrlS': book_data.get('image_url_s', ''),
                    'imageUrlM': book_data.get('image_url_m', ''),
                    'imageUrlL': book_data.get('image_url_l', ''),
                    'avgRating': round(float(book_data['avg_rating']), 2),
                    'ratingCount': int(book_data['rating_count']),
                    'predicted_rating': round(pred['predicted_rating'], 2),
                    'algorithm': 'user_based_cf',
                    'reason': f'基于{similar_user_count}个相似用户的推荐'
                })
        
        return recommendations
    
    def _get_popular_recommendations(self, top_n):
        """获取热门图书推荐（优化版本）"""
        logger.info("生成热门图书推荐")
        
        try:
            if self.books_df is None:
                self.books_df = self.data_loader.load_book_data()
            
            # 选择评分高且评分数量多的图书
            popular_books = self.books_df[
                (self.books_df['rating_count'] >= 10) &
                (self.books_df['avg_rating'] >= 3.5)
            ].nlargest(top_n, ['avg_rating', 'rating_count'])
            
            recommendations = []
            for _, book in popular_books.iterrows():
                recommendations.append({
                    'bookId': book['book_id'],
                    'title': book['title'],
                    'author': book['author'] or '未知作者',
                    'publisher': book.get('publisher', '') or '',
                    'year': int(book['year']) if pd.notna(book['year']) else None,
                    'imageUrlS': book.get('image_url_s', ''),
                    'imageUrlM': book.get('image_url_m', ''),
                    'imageUrlL': book.get('image_url_l', ''),
                    'avgRating': round(float(book['avg_rating']), 2),
                    'ratingCount': int(book['rating_count']),
                    'predicted_rating': round(float(book['avg_rating']), 2),
                    'algorithm': 'popular_fallback',
                    'reason': '热门图书推荐'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取热门推荐失败: {e}")
            return []
    
    def find_similar_users(self, user_id, top_k=20):
        """查找相似用户（对外接口）"""
        similar_users = self.find_similar_users_efficient(user_id, top_k=top_k)
        
        # 转换格式
        result = {}
        for user in similar_users:
            result[user['user_id']] = user['similarity']
        
        return pd.Series(result)
    
    def get_algorithm_info(self):
        """获取算法信息"""
        return {
            'name': '基于用户的协同过滤（内存优化版）',
            'type': 'collaborative_filtering',
            'description': '使用高效算法处理大规模数据，避免内存溢出',
            'parameters': {
                'min_common_items': 5,
                'min_similarity': Config.MIN_SIMILARITY,
                'max_neighbors': 50
            },
            'data_info': {
                'total_ratings': len(self.ratings_df) if self.ratings_df is not None else 0,
                'memory_efficient': True
            }
        }