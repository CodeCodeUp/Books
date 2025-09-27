import numpy as np
import pandas as pd
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from data.data_loader import DataLoader
from utils.cache import RecommendationCache
from config import Config

logger = logging.getLogger(__name__)

class ContentBasedRecommendation:
    """基于内容特征的推荐算法"""
    
    def __init__(self, shared_data_loader=None):
        self.data_loader = shared_data_loader or DataLoader()
        self.cache = RecommendationCache()
        
        # 特征提取器
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        
        # 特征矩阵
        self.book_features = None
        self.feature_names = []
        
    def load_data(self):
        """加载数据"""
        self.ratings_df = self.data_loader.get_ratings_data()
        self.books_df = self.data_loader.get_books_data()
        logger.info("内容特征推荐算法 - 使用共享数据")
        
    def extract_book_features(self):
        """提取图书特征矩阵"""
        logger.info("开始提取图书特征...")
        
        if self.books_df is None:
            self.load_data()
        
        try:
            features_list = []
            
            # 1. 标题TF-IDF特征
            titles = self.books_df['title'].fillna('').astype(str)
            title_features = self.tfidf_vectorizer.fit_transform(titles)
            
            # 2. 作者特征（one-hot编码）
            authors = self.books_df['author'].fillna('Unknown').astype(str)
            author_dummies = pd.get_dummies(authors, prefix='author').values
            
            # 3. 出版社特征（one-hot编码）
            publishers = self.books_df['publisher'].fillna('Unknown').astype(str)
            publisher_dummies = pd.get_dummies(publishers, prefix='publisher').values
            
            # 4. 年份特征（数值标准化）
            years = self.books_df['year'].fillna(2000).astype(float)
            year_features = self.scaler.fit_transform(years.values.reshape(-1, 1))
            
            # 5. 评分特征
            avg_ratings = self.books_df['avg_rating'].fillna(0).astype(float)
            rating_features = avg_ratings.values.reshape(-1, 1)
            
            # 合并所有特征
            import scipy.sparse as sp
            all_features = sp.hstack([
                title_features,
                sp.csr_matrix(author_dummies),
                sp.csr_matrix(publisher_dummies),
                sp.csr_matrix(year_features),
                sp.csr_matrix(rating_features)
            ])
            
            self.book_features = all_features
            
            logger.info(f"图书特征提取完成: {all_features.shape}")
            return True
            
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return False
    
    def build_user_profile(self, user_id):
        """构建用户兴趣画像"""
        try:
            # 获取用户评分历史
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
            
            if user_ratings.empty:
                return None
            
            # 获取用户评分过的图书特征
            rated_books = user_ratings.merge(self.books_df, on='book_id', how='left')
            
            # 构建用户偏好特征
            user_profile = {
                'favorite_authors': {},
                'favorite_publishers': {},
                'year_preference': [],
                'rating_tendency': user_ratings['rating'].mean(),
                'total_books': len(user_ratings)
            }
            
            # 作者偏好（加权平均）
            for _, book in rated_books.iterrows():
                author = book['author'] or 'Unknown'
                rating = book['rating']
                
                if author not in user_profile['favorite_authors']:
                    user_profile['favorite_authors'][author] = []
                user_profile['favorite_authors'][author].append(rating)
            
            # 计算作者平均评分
            for author in user_profile['favorite_authors']:
                ratings_list = user_profile['favorite_authors'][author]
                user_profile['favorite_authors'][author] = np.mean(ratings_list)
            
            # 年份偏好
            user_profile['year_preference'] = rated_books['year'].dropna().values
            
            return user_profile
            
        except Exception as e:
            logger.error(f"构建用户画像失败: {e}")
            return None
    
    def get_content_based_recommendations(self, user_id, top_n=10):
        """基于内容特征的推荐"""
        logger.info(f"为用户 {user_id} 生成基于内容的推荐...")
        
        try:
            # 确保特征已提取
            if self.book_features is None:
                if not self.extract_book_features():
                    return []
            
            # 构建用户画像
            user_profile = self.build_user_profile(user_id)
            if user_profile is None:
                logger.warning(f"用户 {user_id} 没有评分历史，返回热门图书")
                return self._get_popular_books_by_content(top_n)
            
            # 获取用户已评分的图书
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
            rated_book_ids = set(user_ratings['book_id'].values)
            
            # 计算推荐分数
            recommendations = []
            
            for idx, book in self.books_df.iterrows():
                book_id = book['book_id']
                
                if book_id in rated_book_ids:
                    continue  # 跳过已评分图书
                
                # 计算内容相似度分数
                content_score = self._calculate_content_score(book, user_profile)
                
                if content_score > 0.1:  # 分数阈值
                    recommendations.append({
                        'bookId': book_id,
                        'title': book['title'],
                        'author': book['author'] or '未知作者',
                        'publisher': book.get('publisher', '') or '',
                        'year': int(book['year']) if pd.notna(book['year']) else None,
                        'imageUrlS': book.get('image_url_s', ''),
                        'imageUrlM': book.get('image_url_m', ''),
                        'imageUrlL': book.get('image_url_l', ''),
                        'avgRating': round(float(book['avg_rating']), 2),
                        'ratingCount': int(book['rating_count']),
                        'content_score': round(content_score, 3),
                        'algorithm': 'content_based',
                        'reason': f'基于您的阅读偏好和图书内容特征'
                    })
            
            # 按分数排序
            recommendations.sort(key=lambda x: x['content_score'], reverse=True)
            
            logger.info(f"基于内容特征生成 {len(recommendations[:top_n])} 个推荐")
            return recommendations[:top_n]
            
        except Exception as e:
            logger.error(f"内容特征推荐失败: {e}")
            return []
    
    def _calculate_content_score(self, book, user_profile):
        """计算图书与用户偏好的内容匹配度"""
        try:
            score = 0.0
            
            # 1. 作者偏好匹配 (权重40%)
            author = book['author'] or 'Unknown'
            if author in user_profile['favorite_authors']:
                author_score = user_profile['favorite_authors'][author] / 5.0  # 标准化到0-1
                score += 0.4 * author_score
            
            # 2. 年份偏好匹配 (权重20%)
            if pd.notna(book['year']) and len(user_profile['year_preference']) > 0:
                book_year = int(book['year'])
                year_diff = abs(book_year - np.mean(user_profile['year_preference']))
                year_score = max(0, 1 - year_diff / 50)  # 年份差距归一化
                score += 0.2 * year_score
            
            # 3. 质量匹配 (权重30%)
            book_rating = float(book['avg_rating'])
            user_tendency = user_profile['rating_tendency']
            rating_diff = abs(book_rating - user_tendency)
            rating_score = max(0, 1 - rating_diff / 5)
            score += 0.3 * rating_score
            
            # 4. 流行度调节 (权重10%)
            rating_count = int(book['rating_count'])
            popularity_score = min(1.0, rating_count / 100)  # 评分数越多越可靠
            score += 0.1 * popularity_score
            
            return score
            
        except Exception as e:
            logger.error(f"计算内容分数失败: {e}")
            return 0.0
    
    def get_similar_books_by_content(self, target_book_id, top_k=10):
        """基于内容特征的相似图书推荐（性能优化版本）"""
        logger.info(f"基于内容特征查找与图书 {target_book_id} 相似的图书...")
        
        try:
            # 获取目标图书信息
            target_book = self.books_df[self.books_df['book_id'] == target_book_id]
            if target_book.empty:
                return []
            
            target_book_data = target_book.iloc[0]
            logger.info(f"目标图书: {target_book_data['title']} - {target_book_data['author']}")
            
            # 1. 预筛选候选图书（避免与14万本图书比较）
            candidate_books = self._get_content_candidates(target_book_data)
            logger.info(f"预筛选候选图书: {len(candidate_books)} 本（从14万本筛选）")
            
            if len(candidate_books) == 0:
                logger.warning("没有找到合适的候选图书")
                return []
            
            # 2. 只对候选图书计算详细相似度
            similarities = []
            
            for _, book in candidate_books.iterrows():
                if book['book_id'] == target_book_id:
                    continue
                
                # 计算内容相似度
                similarity = self._calculate_book_content_similarity(target_book_data, book)
                
                if similarity > 0.2:  # 相似度阈值
                    similarities.append({
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
                        'similarity': round(similarity, 3),
                        'reason': f'内容特征相似度{similarity:.2f}'
                    })
            
            # 按相似度排序
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"基于内容特征找到 {len(similarities[:top_k])} 本相似图书")
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"内容特征相似图书推荐失败: {e}")
            return []
    
    def _get_content_candidates(self, target_book):
        """预筛选候选图书（性能优化关键）"""
        try:
            candidate_books = pd.DataFrame()
            
            # 1. 同作者图书（最高优先级）
            if pd.notna(target_book['author']):
                same_author = self.books_df[
                    (self.books_df['author'] == target_book['author']) &
                    (self.books_df['book_id'] != target_book['book_id'])
                ]
                candidate_books = pd.concat([candidate_books, same_author], ignore_index=True)
                logger.info(f"找到同作者图书: {len(same_author)} 本")
            
            # 2. 同出版社图书
            if pd.notna(target_book['publisher']):
                same_publisher = self.books_df[
                    (self.books_df['publisher'] == target_book['publisher']) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(candidate_books['book_id']))  # 去重
                ]
                candidate_books = pd.concat([candidate_books, same_publisher], ignore_index=True)
                logger.info(f"找到同出版社图书: {len(same_publisher)} 本")
            
            # 3. 相近年代图书（±10年）
            if pd.notna(target_book['year']):
                target_year = int(target_book['year'])
                nearby_years = self.books_df[
                    (self.books_df['year'] >= target_year - 10) &
                    (self.books_df['year'] <= target_year + 10) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(candidate_books['book_id']))  # 去重
                ]
                # 限制相近年代的数量，避免过多
                nearby_years_sample = nearby_years.nlargest(500, ['avg_rating', 'rating_count'])
                candidate_books = pd.concat([candidate_books, nearby_years_sample], ignore_index=True)
                logger.info(f"找到相近年代图书: {len(nearby_years_sample)} 本")
            
            # 4. 高质量图书补充（如果候选不够）
            if len(candidate_books) < 100:
                quality_books = self.books_df[
                    (self.books_df['avg_rating'] >= 4.0) &
                    (self.books_df['rating_count'] >= 20) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(candidate_books['book_id']))  # 去重
                ].head(200)  # 限制数量
                candidate_books = pd.concat([candidate_books, quality_books], ignore_index=True)
                logger.info(f"补充高质量图书: {len(quality_books)} 本")
            
            # 去重并限制最终候选数量
            candidate_books = candidate_books.drop_duplicates(subset=['book_id']).head(1000)
            
            logger.info(f"最终候选图书数量: {len(candidate_books)} 本")
            return candidate_books
            
        except Exception as e:
            logger.error(f"预筛选候选图书失败: {e}")
            return pd.DataFrame()
    
    def _calculate_book_content_similarity(self, book1, book2):
        """计算两本图书的内容相似度"""
        try:
            similarity = 0.0
            
            # 1. 作者相似度 (权重50%)
            if book1['author'] == book2['author'] and pd.notna(book1['author']):
                similarity += 0.5
            
            # 2. 出版社相似度 (权重20%)
            if book1['publisher'] == book2['publisher'] and pd.notna(book1['publisher']):
                similarity += 0.2
            
            # 3. 年份相似度 (权重20%)
            if pd.notna(book1['year']) and pd.notna(book2['year']):
                year_diff = abs(int(book1['year']) - int(book2['year']))
                year_similarity = max(0, 1 - year_diff / 20)  # 20年内认为相似
                similarity += 0.2 * year_similarity
            
            # 4. 评分相似度 (权重10%)
            if pd.notna(book1['avg_rating']) and pd.notna(book2['avg_rating']):
                rating_diff = abs(float(book1['avg_rating']) - float(book2['avg_rating']))
                rating_similarity = max(0, 1 - rating_diff / 2)  # 2分内认为相似
                similarity += 0.1 * rating_similarity
            
            return similarity
            
        except Exception as e:
            logger.error(f"计算图书内容相似度失败: {e}")
            return 0.0
    
    def get_content_based_recommendations(self, user_id, top_n=10):
        """基于内容特征的推荐 - 支持新用户和协同过滤失败场景"""
        logger.info(f"为用户 {user_id} 生成基于内容的推荐...")
        
        try:
            # 1. 获取用户基础信息（地区、年龄、国家）
            user_info = self._get_user_basic_info(user_id)
            
            if not user_info or not self._has_valid_user_features(user_info):
                logger.info(f"用户 {user_id} 没有有效的特征信息，返回热门图书")
                return self._get_top_quality_books(top_n)
            
            logger.info(f"用户特征: 年龄={user_info.get('age')}, 国家={user_info.get('country')}, 地区={user_info.get('location')}")
            
            # 2. 基于用户特征推荐图书
            recommendations = self._recommend_by_user_features(user_info, top_n)
            
            logger.info(f"基于用户特征生成 {len(recommendations)} 个推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"内容特征推荐失败: {e}")
            return self._get_top_quality_books(top_n)
    
    def _get_user_basic_info(self, user_id):
        """获取用户基础信息"""
        try:
            user_query = """
            SELECT user_id, age, country, location
            FROM users 
            WHERE user_id = %(user_id)s
            """
            
            user_df = pd.read_sql(user_query, self.data_loader.engine, params={'user_id': user_id})
            
            if user_df.empty:
                return None
            
            return user_df.iloc[0].to_dict()
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def _has_valid_user_features(self, user_info):
        """检查用户是否有有效的特征信息"""
        return (
            (user_info.get('age') is not None and user_info.get('age') > 0) or
            (user_info.get('country') is not None and str(user_info.get('country')).strip() != '') or
            (user_info.get('location') is not None and str(user_info.get('location')).strip() != '')
        )
    
    def _recommend_by_user_features(self, user_info, top_n):
        """基于用户特征推荐图书"""
        try:
            recommendations = []
            
            # 获取高质量图书池
            quality_books = self.books_df[
                (self.books_df['rating_count'] >= 5) &
                (self.books_df['avg_rating'] >= 3.0)
            ].copy()
            
            # 为每本书计算与用户特征的匹配度
            for idx, book in quality_books.iterrows():
                match_score = self._calculate_user_book_match(user_info, book)
                
                if match_score > 0.1:  # 匹配度阈值
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
                        'content_score': round(match_score, 3),
                        'algorithm': 'content_based_user_profile',
                        'reason': self._generate_recommendation_reason(user_info, book, match_score)
                    })
            
            # 按匹配度排序
            recommendations.sort(key=lambda x: x['content_score'], reverse=True)
            
            return recommendations[:top_n]
            
        except Exception as e:
            logger.error(f"基于用户特征推荐失败: {e}")
            return self._get_top_quality_books(top_n)
    
    def _calculate_user_book_match(self, user_info, book):
        """计算用户特征与图书的匹配度"""
        try:
            score = 0.0
            
            # 1. 年龄匹配 (权重40%)
            user_age = user_info.get('age')
            if user_age and user_age > 0:
                book_year = book.get('year')
                if pd.notna(book_year):
                    # 年轻用户偏好新书，年长用户偏好经典
                    if user_age < 25:
                        age_score = 1.0 if book_year >= 2000 else 0.5
                    elif user_age < 40:
                        age_score = 1.0 if book_year >= 1990 else 0.7
                    else:
                        age_score = 1.0 if book_year <= 2000 else 0.8
                    
                    score += 0.4 * age_score
            
            # 2. 国家/文化匹配 (权重30%)
            user_country = user_info.get('country', '').lower()
            book_title = str(book.get('title', '')).lower()
            book_author = str(book.get('author', '')).lower()
            
            if user_country:
                # 简单的文化匹配规则
                if user_country in ['usa', 'canada', 'uk', 'australia']:
                    # 英语国家用户偏好英语作品
                    if any(name in book_author for name in ['john', 'david', 'michael', 'james', 'robert']):
                        score += 0.3 * 0.8
                elif user_country in ['germany', 'france', 'spain', 'italy']:
                    # 欧洲用户偏好欧洲文学
                    if any(word in book_title for word in ['europe', 'paris', 'london', 'berlin']):
                        score += 0.3 * 0.8
                else:
                    # 其他国家用户偏好国际经典
                    score += 0.3 * 0.5
            
            # 3. 图书质量评分 (权重30%)
            quality_score = float(book.get('avg_rating', 0)) / 5.0
            popularity_score = min(1.0, int(book.get('rating_count', 0)) / 100)
            combined_quality = (quality_score + popularity_score) / 2
            score += 0.3 * combined_quality
            
            return score
            
        except Exception as e:
            logger.error(f"计算用户图书匹配度失败: {e}")
            return 0.0
    
    def _generate_recommendation_reason(self, user_info, book, match_score):
        """生成推荐理由"""
        reasons = []
        
        user_age = user_info.get('age')
        if user_age:
            if user_age < 25:
                reasons.append("适合年轻读者")
            elif user_age > 40:
                reasons.append("适合成熟读者")
        
        user_country = user_info.get('country')
        if user_country:
            reasons.append(f"推荐给{user_country}读者")
        
        book_rating = book.get('avg_rating', 0)
        if book_rating >= 4.0:
            reasons.append("高评分优质图书")
        
        return "、".join(reasons) if reasons else f"内容特征匹配度{match_score:.2f}"
    
    def _get_top_quality_books(self, top_n):
        """获取前10本评分最高且人数最多的图书（新用户无特征时使用）"""
        logger.info("返回评分最高且评价人数最多的热门图书")
        
        try:
            # 选择评分高且评分人数多的图书
            top_books = self.books_df[
                (self.books_df['rating_count'] >= 20) &  # 至少20人评分
                (self.books_df['avg_rating'] >= 4.0)     # 评分4.0以上
            ].nlargest(top_n, ['avg_rating', 'rating_count'])
            
            recommendations = []
            for _, book in top_books.iterrows():
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
                    'content_score': round(float(book['avg_rating']) / 5.0, 3),
                    'algorithm': 'top_quality_books',
                    'reason': f'高质量热门图书（{book["avg_rating"]:.1f}分，{book["rating_count"]}人评价）'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取热门优质图书失败: {e}")
            return []
    
    def get_algorithm_info(self):
        """获取算法信息"""
        return {
            'name': '基于内容特征的推荐',
            'type': 'content_based_filtering',
            'description': '基于图书内容特征的相似性推荐，解决冷启动问题',
            'features': [
                '作者特征匹配',
                '标题关键词相似度',
                '出版社特征',
                '年代特征',
                '评分质量特征'
            ],
            'advantages': [
                '无冷启动问题',
                '推荐解释性强',
                '不依赖用户行为'
            ]
        }