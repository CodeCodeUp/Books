import numpy as np
import pandas as pd
import logging
from algorithms.collaborative_filtering import UserBasedCollaborativeFiltering
from algorithms.item_based_cf import ItemBasedCollaborativeFiltering
from algorithms.content_based import ContentBasedRecommendation
from config import Config

logger = logging.getLogger(__name__)

class HybridRecommendation:
    """混合推荐策略 - 协同过滤与内容特征混合"""
    
    def __init__(self, shared_data_loader):
        # 使用共享的算法实例，避免重复初始化
        self.data_loader = shared_data_loader
        
        # 注意：这里不创建新实例，而是在需要时使用外部传入的实例
        self.user_cf = None  # 将在外部设置
        self.item_cf = None  # 将在外部设置
        self.content_cf = ContentBasedRecommendation(shared_data_loader)
        
    def load_data(self):
        """加载数据"""
        # 只加载内容特征算法的数据，协同过滤算法已经加载过了
        self.content_cf.load_data()
        logger.info("混合推荐算法 - 内容特征数据加载完成")
    
    def get_hybrid_user_recommendations(self, user_id, top_n=10, cf_ratio=0.7):
        """混合推荐：用户协同过滤 + 内容特征 (推荐页面使用)"""
        logger.info(f"为用户 {user_id} 生成混合推荐 (用户协同{cf_ratio:.0%} + 内容特征{1-cf_ratio:.0%})")
        
        try:
            # 1. 检查用户是否有评分历史
            user_ratings = self.user_cf.ratings_df[self.user_cf.ratings_df['user_id'] == user_id]
            has_ratings = not user_ratings.empty
            
            # 2. 检查用户是否有基础特征信息
            user_info = self.content_cf._get_user_basic_info(user_id)
            has_features = user_info and self.content_cf._has_valid_user_features(user_info)
            
            logger.info(f"用户状态: 有评分历史={has_ratings}, 有特征信息={has_features}")
            
            # 3. 根据用户状态决定推荐策略
            if has_ratings and has_features:
                # 情况1: 既有评分又有特征 - 混合推荐
                logger.info("用户有评分历史和特征信息，使用混合推荐")
                cf_recommendations = self._get_cf_recommendations_no_fallback(user_id, top_n * 2)
                content_recommendations = self.content_cf._recommend_by_user_features(user_info, top_n * 2)
                
                if cf_recommendations and content_recommendations:
                    return self._mix_recommendations(cf_recommendations, content_recommendations, cf_ratio, top_n)
                elif cf_recommendations:
                    return cf_recommendations[:top_n]
                elif content_recommendations:
                    return content_recommendations[:top_n]
                else:
                    return self._get_fallback_recommendations(top_n)
                    
            elif has_ratings:
                # 情况2: 有评分无特征 - 纯协同过滤
                logger.info("用户有评分历史但无特征信息，使用协同过滤")
                cf_recommendations = self._get_cf_recommendations_no_fallback(user_id, top_n)
                return cf_recommendations if cf_recommendations else self._get_fallback_recommendations(top_n)
                
            elif has_features:
                # 情况3: 有特征无评分 - 基于用户特征推荐
                logger.info("用户有特征信息但无评分历史，使用基于特征的内容推荐")
                return self.content_cf._recommend_by_user_features(user_info, top_n)
                
            else:
                # 情况4: 既无评分又无特征 - 优质热门图书
                logger.info("用户既无评分历史又无特征信息，返回优质热门图书")
                return self._get_fallback_recommendations(top_n)
            
        except Exception as e:
            logger.error(f"混合推荐失败: {e}")
            return self._get_fallback_recommendations(top_n)
    
    def _get_cf_recommendations_no_fallback(self, user_id, top_n):
        """获取协同过滤推荐，不使用热门降级"""
        try:
            # 检查用户是否在评分矩阵中
            user_ratings = self.user_cf.ratings_df[self.user_cf.ratings_df['user_id'] == user_id]
            if user_ratings.empty:
                return []
            
            # 尝试找相似用户
            similar_users = self.user_cf.find_similar_users_efficient(user_id)
            if not similar_users:
                return []
            
            # 生成协同过滤推荐
            return self.user_cf._generate_personalized_recommendations(user_id, top_n, 3.0)
            
        except Exception as e:
            logger.error(f"获取协同过滤推荐失败: {e}")
            return []
    
    def _get_fallback_recommendations(self, top_n):
        """统一的降级推荐：前10本评分最高且人数最多的图书"""
        logger.info("使用统一降级策略：返回评分最高且评价人数最多的优质图书")
        return self.content_cf._get_top_quality_books(top_n)
    
    def get_hybrid_similar_books(self, target_book_id, top_k=6, cf_ratio=0.7):
        """混合相似图书：物品协同过滤 + 内容特征 (图书详情页使用)"""
        logger.info(f"为图书 {target_book_id} 生成混合相似推荐 (物品协同{cf_ratio:.0%} + 内容特征{1-cf_ratio:.0%})")
        
        try:
            # 1. 尝试物品协同过滤
            cf_similar = self.item_cf.get_similar_books_for_item(target_book_id, top_k * 2)
            
            # 2. 尝试内容特征相似
            content_similar = self.content_cf.get_similar_books_by_content(target_book_id, top_k * 2)
            
            # 3. 混合策略
            if cf_similar and content_similar:
                logger.info("物品协同过滤和内容特征都有结果，按7:3混合")
                mixed_similar = self._mix_recommendations(
                    cf_similar, content_similar, cf_ratio, top_k
                )
            elif cf_similar:
                logger.info("只有物品协同过滤有结果，使用协同过滤")
                mixed_similar = cf_similar[:top_k]
            elif content_similar:
                logger.info("只有内容特征有结果，使用内容特征")
                mixed_similar = content_similar[:top_k]
            else:
                logger.warning("两种算法都无结果，返回同作者图书")
                mixed_similar = self._get_same_author_books(target_book_id, top_k)
            
            logger.info(f"混合相似图书推荐完成，返回 {len(mixed_similar)} 个推荐")
            return mixed_similar
            
        except Exception as e:
            logger.error(f"混合相似图书推荐失败: {e}")
            return []
    
    def _mix_recommendations(self, primary_recs, secondary_recs, primary_ratio, total_count):
        """按比例混合两个推荐结果"""
        try:
            primary_count = int(total_count * primary_ratio)
            secondary_count = total_count - primary_count
            
            # 去重：移除在主推荐中已存在的图书
            primary_book_ids = {rec['bookId'] for rec in primary_recs}
            filtered_secondary = [
                rec for rec in secondary_recs 
                if rec['bookId'] not in primary_book_ids
            ]
            
            # 组合结果
            mixed = []
            mixed.extend(primary_recs[:primary_count])
            mixed.extend(filtered_secondary[:secondary_count])
            
            logger.info(f"混合推荐: 主算法{len(primary_recs[:primary_count])}个 + 辅助算法{len(filtered_secondary[:secondary_count])}个")
            
            return mixed[:total_count]
            
        except Exception as e:
            logger.error(f"混合推荐失败: {e}")
            return primary_recs[:total_count]
    
    def _get_popular_fallback(self, top_n):
        """热门图书后备推荐（使用内容特征的优质图书）"""
        return self.content_cf._get_top_quality_books(top_n)
    
    def _get_same_author_books(self, target_book_id, top_k):
        """同作者图书推荐（最后的降级策略）"""
        try:
            target_book = self.content_cf.books_df[
                self.content_cf.books_df['book_id'] == target_book_id
            ]
            
            if target_book.empty:
                return []
            
            target_author = target_book.iloc[0]['author']
            if pd.isna(target_author):
                return []
            
            same_author_books = self.content_cf.books_df[
                (self.content_cf.books_df['author'] == target_author) &
                (self.content_cf.books_df['book_id'] != target_book_id)
            ].nlargest(top_k, ['avg_rating', 'rating_count'])
            
            recommendations = []
            for _, book in same_author_books.iterrows():
                recommendations.append({
                    'bookId': book['book_id'],
                    'title': book['title'],
                    'author': book['author'],
                    'publisher': book.get('publisher', '') or '',
                    'year': int(book['year']) if pd.notna(book['year']) else None,
                    'imageUrlS': book.get('image_url_s', ''),
                    'imageUrlM': book.get('image_url_m', ''),
                    'imageUrlL': book.get('image_url_l', ''),
                    'avgRating': round(float(book['avg_rating']), 2),
                    'ratingCount': int(book['rating_count']),
                    'algorithm': 'same_author_fallback',
                    'reason': f'同作者作品推荐'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"同作者图书推荐失败: {e}")
            return []