import numpy as np
import pandas as pd
import logging
from sklearn.metrics.pairwise import cosine_similarity
from data.data_loader import DataLoader
from utils.cache import RecommendationCache
from config import Config

logger = logging.getLogger(__name__)

class ItemBasedCollaborativeFiltering:
    """基于物品的协同过滤推荐算法"""
    
    def __init__(self, shared_data_loader=None):
        self.data_loader = shared_data_loader or DataLoader()
        self.cache = RecommendationCache()
        self.item_similarity_cache = {}  # 图书相似度缓存
        
    def load_data(self):
        """使用共享的数据加载器"""
        # 获取已加载的数据
        self.ratings_df = self.data_loader.get_ratings_data()
        self.books_df = self.data_loader.get_books_data()
        
        logger.info("物品协同过滤算法 - 使用共享数据")
    
    def calculate_item_similarity(self, item1_id, item2_id):
        """计算两本图书的相似度"""
        cache_key = f"{item1_id}_{item2_id}"
        
        # 检查缓存
        if cache_key in self.item_similarity_cache:
            return self.item_similarity_cache[cache_key]
        
        try:
            # 获取两本书的评分数据
            item1_ratings = self.ratings_df[self.ratings_df['book_id'] == item1_id]
            item2_ratings = self.ratings_df[self.ratings_df['book_id'] == item2_id]
            
            if item1_ratings.empty or item2_ratings.empty:
                similarity = 0.0
            else:
                # 找到对两本书都评分的用户
                item1_users = set(item1_ratings['user_id'].values)
                item2_users = set(item2_ratings['user_id'].values)
                common_users = item1_users & item2_users
                
                if len(common_users) < 2:  # 至少需要2个用户都评分过
                    similarity = 0.0
                else:
                    # 创建共同用户的评分向量
                    item1_ratings_dict = dict(zip(item1_ratings['user_id'], item1_ratings['rating']))
                    item2_ratings_dict = dict(zip(item2_ratings['user_id'], item2_ratings['rating']))
                    
                    item1_vector = [item1_ratings_dict[user] for user in common_users]
                    item2_vector = [item2_ratings_dict[user] for user in common_users]
                    
                    # 计算余弦相似度
                    item1_array = np.array(item1_vector).reshape(1, -1)
                    item2_array = np.array(item2_vector).reshape(1, -1)
                    
                    similarity = cosine_similarity(item1_array, item2_array)[0][0]
                    similarity = max(0.0, similarity)
            
            # 缓存结果
            self.item_similarity_cache[cache_key] = similarity
            self.item_similarity_cache[f"{item2_id}_{item1_id}"] = similarity  # 对称缓存
            
            return similarity
            
        except Exception as e:
            logger.error(f"计算图书相似度失败: {e}")
            return 0.0
    
    def get_similar_books_for_item(self, target_book_id, top_k=10):
        """获取与目标图书相似的图书（批量优化版本）"""
        logger.info(f"基于评分模式查找与图书 {target_book_id} 相似的图书...")
        
        try:
            # 1. 获取评分过目标图书的用户
            target_ratings = self.ratings_df[self.ratings_df['book_id'] == target_book_id]
            
            if target_ratings.empty:
                logger.warning(f"图书 {target_book_id} 没有评分数据")
                return []
            
            target_users = set(target_ratings['user_id'].values)
            target_ratings_dict = dict(zip(target_ratings['user_id'], target_ratings['rating']))
            logger.info(f"目标图书有 {len(target_users)} 个用户评分")
            
            # 2. 快速筛选候选图书
            candidate_ratings = self.ratings_df[
                (self.ratings_df['user_id'].isin(target_users)) &
                (self.ratings_df['book_id'] != target_book_id)
            ]
            
            candidate_books = candidate_ratings['book_id'].unique()
            logger.info(f"候选图书数量: {len(candidate_books)} 本")
            
            # 3. 批量计算相似度（优化版本）
            similarities = []
            
            # 按候选图书分组，避免重复查询
            candidate_ratings_grouped = candidate_ratings.groupby('book_id')
            
            for other_book_id, other_book_ratings in candidate_ratings_grouped:
                # 直接使用分组后的数据，避免重复过滤
                other_users = set(other_book_ratings['user_id'].values)
                common_users = target_users & other_users
                
                if len(common_users) >= 2:  # 至少2个共同用户
                    # 构建共同用户的评分向量
                    target_vector = [target_ratings_dict[user] for user in common_users]
                    other_ratings_dict = dict(zip(other_book_ratings['user_id'], other_book_ratings['rating']))
                    other_vector = [other_ratings_dict[user] for user in common_users]
                    
                    # 计算余弦相似度
                    target_array = np.array(target_vector).reshape(1, -1)
                    other_array = np.array(other_vector).reshape(1, -1)
                    
                    similarity = cosine_similarity(target_array, other_array)[0][0]
                    similarity = max(0.0, similarity)
                    
                    if similarity > 0.1:
                        similarities.append({
                            'book_id': other_book_id,
                            'similarity': similarity,
                            'common_users_count': len(common_users)
                        })
            
            logger.info(f"批量计算完成，找到 {len(similarities)} 本相似图书")
            
            # 4. 按相似度排序
            similarities.sort(key=lambda x: (x['similarity'], x['common_users_count']), reverse=True)
            top_similar = similarities[:top_k]
            
            # 5. 补充图书详细信息
            result = []
            for sim in top_similar:
                book_info = self.books_df[self.books_df['book_id'] == sim['book_id']]
                if not book_info.empty:
                    book_data = book_info.iloc[0]
                    result.append({
                        'bookId': sim['book_id'],
                        'title': book_data['title'],
                        'author': book_data['author'] or '未知作者',
                        'publisher': book_data.get('publisher', '') or '',
                        'year': int(book_data['year']) if pd.notna(book_data['year']) else None,
                        'imageUrlS': book_data.get('image_url_s', ''),
                        'imageUrlM': book_data.get('image_url_m', ''),
                        'imageUrlL': book_data.get('image_url_l', ''),
                        'avgRating': round(float(book_data['avg_rating']), 2),
                        'ratingCount': int(book_data['rating_count']),
                        'similarity': round(sim['similarity'], 3),
                        'common_users': sim['common_users_count'],
                        'reason': f'基于{sim["common_users_count"]}个共同用户的评分模式，相似度{sim["similarity"]:.2f}'
                    })
            
            logger.info(f"最终返回 {len(result)} 本相似图书")
            return result
            
        except Exception as e:
            logger.error(f"查找相似图书失败: {e}")
            return []
    
    def predict_item_rating(self, user_id, target_item_id, user_ratings_dict, similar_items):
        """预测用户对目标图书的评分"""
        try:
            if not similar_items:
                return 0.0
            
            weighted_sum = 0.0
            similarity_sum = 0.0
            
            for similar_item in similar_items:
                similar_item_id = similar_item['item_id']
                similarity = similar_item['similarity']
                
                if similar_item_id in user_ratings_dict:
                    user_rating = user_ratings_dict[similar_item_id]
                    weighted_sum += similarity * user_rating
                    similarity_sum += abs(similarity)
            
            if similarity_sum > 0:
                predicted_rating = weighted_sum / similarity_sum
                return max(0.0, min(5.0, predicted_rating))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"预测图书评分失败: {e}")
            return 0.0
    
    def get_recommendations(self, user_id, top_n=None, min_rating=3.0):
        """基于物品的协同过滤推荐"""
        if top_n is None:
            top_n = Config.DEFAULT_TOP_N
            
        logger.info(f"=== 为用户 {user_id} 生成物品协同过滤推荐 ===")
        
        # 检查缓存
        cached_recommendations = self.cache.load_recommendations(user_id)
        if cached_recommendations:
            logger.info(f"从缓存返回用户 {user_id} 的推荐结果")
            return cached_recommendations[:top_n]
        
        try:
            # 确保数据已加载
            if not self.data_initialized:
                self.load_data()
            
            # 获取用户评分历史
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
            
            if user_ratings.empty:
                logger.warning(f"用户 {user_id} 没有评分记录，返回热门推荐")
                return self._get_popular_recommendations(top_n)
            
            user_rated_items = set(user_ratings['book_id'].values)
            user_ratings_dict = dict(zip(user_ratings['book_id'], user_ratings['rating']))
            
            logger.info(f"用户 {user_id} 评分了 {len(user_rated_items)} 本图书")
            
            # 获取候选图书（用户未评分的图书）
            all_books = set(self.books_df['book_id'].values)
            candidate_items = all_books - user_rated_items
            
            logger.info(f"候选图书数量: {len(candidate_items):,}")
            
            # 为候选图书预测评分
            predictions = []
            processed_count = 0
            
            for candidate_item_id in list(candidate_items)[:1000]:  # 限制候选数量提升性能
                similar_items = self.find_similar_items(candidate_item_id, user_rated_items)
                
                if similar_items:
                    predicted_rating = self.predict_item_rating(
                        user_id, candidate_item_id, user_ratings_dict, similar_items
                    )
                    
                    if predicted_rating >= min_rating:
                        predictions.append({
                            'book_id': candidate_item_id,
                            'predicted_rating': predicted_rating,
                            'similar_items_count': len(similar_items)
                        })
                
                processed_count += 1
                if processed_count % 100 == 0:
                    logger.info(f"已处理 {processed_count} 本候选图书...")
            
            # 按预测评分排序
            predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
            top_predictions = predictions[:top_n]
            
            # 补充图书详细信息
            recommendations = self._enrich_recommendations(top_predictions)
            
            # 缓存结果
            if recommendations:
                self.cache.save_recommendations(user_id, recommendations, 'item_based_cf')
            
            logger.info(f"物品协同过滤成功生成 {len(recommendations)} 个推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"物品协同过滤推荐失败: {e}")
            return self._get_popular_recommendations(top_n)
    
    def _enrich_recommendations(self, predictions):
        """补充推荐结果的图书信息"""
        recommendations = []
        
        for pred in predictions:
            book_info = self.books_df[
                self.books_df['book_id'] == pred['book_id']
            ]
            
            if not book_info.empty:
                book_data = book_info.iloc[0]
                recommendations.append({
                    'bookId': pred['book_id'],
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
                    'algorithm': 'item_based_cf',
                    'reason': f'基于您评分图书的相似图书推荐'
                })
        
        return recommendations
    
    def _get_popular_recommendations(self, top_n):
        """获取热门图书推荐（后备方案）"""
        logger.info("使用热门图书作为推荐")
        
        try:
            if self.books_df is None:
                self.books_df = self.data_loader.get_books_data()
            
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
    
    def get_algorithm_info(self):
        """获取算法信息"""
        return {
            'name': '基于物品的协同过滤',
            'type': 'item_based_collaborative_filtering',
            'description': '基于图书间相似度推荐，稳定性更好',
            'parameters': {
                'min_common_users': 2,
                'min_similarity': 0.1,
                'max_candidates': 1000
            },
            'advantages': [
                '推荐结果稳定',
                '计算相对简单', 
                '适合图书推荐场景'
            ]
        }