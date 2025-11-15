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
        """
        提取图书特征矩阵（TF-IDF优化版本）

        特征组成：
        1. TF-IDF文本特征（标题+作者+出版社组合）- 1500维
        2. 年份标准化 - 1维
        3. 评分标准化 - 1维
        总维度：约1502维
        """
        logger.info("开始提取图书特征（TF-IDF方法）...")

        if self.books_df is None:
            self.load_data()

        try:
            import scipy.sparse as sp

            # ===== 核心：TF-IDF文本特征 =====
            # 组合文本：标题 + 作者 + 出版社
            # 这样可以一次性提取所有文本特征，避免维度爆炸
            combined_text = (
                self.books_df['title'].fillna('') + ' ' +
                self.books_df['author'].fillna('') + ' ' +
                self.books_df['publisher'].fillna('')
            )

            # TF-IDF提取（1500维）
            tfidf_features = self.tfidf_vectorizer.fit_transform(combined_text)
            logger.info(f"TF-IDF特征维度: {tfidf_features.shape[1]}")

            # ===== 辅助：数值特征（标准化） =====
            # 年份标准化
            years = self.books_df['year'].fillna(2000).astype(float)
            year_features = self.scaler.fit_transform(years.values.reshape(-1, 1))

            # 评分标准化
            ratings = self.books_df['avg_rating'].fillna(0).astype(float)
            rating_scaler = StandardScaler()
            rating_features = rating_scaler.fit_transform(ratings.values.reshape(-1, 1))

            # ===== 合并所有特征 =====
            self.book_features = sp.hstack([
                tfidf_features,                    # 1500维（主要特征）
                sp.csr_matrix(year_features),      # 1维
                sp.csr_matrix(rating_features)     # 1维
            ])

            logger.info(f"图书特征提取完成: {self.book_features.shape}")
            logger.info(f"稀疏矩阵非零元素: {self.book_features.nnz:,}")
            logger.info(f"内存占用估算: {self.book_features.data.nbytes / 1024 / 1024:.1f} MB")

            return True

        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def get_content_based_recommendations(self, user_id, top_n=10):
        """
        基于TF-IDF向量的内容特征推荐

        原理：
        1. 根据用户评分历史，构建用户的TF-IDF向量（加权平均）
        2. 计算用户向量与所有候选图书向量的余弦相似度
        3. 返回相似度最高的Top-N图书

        参数:
            user_id: 用户ID
            top_n: 推荐数量

        返回:
            list: 推荐列表
        """
        logger.info(f"为用户 {user_id} 生成基于TF-IDF的内容推荐...")

        try:
            # 1. 确保特征矩阵已提取
            if self.book_features is None:
                logger.warning("特征矩阵未提取，开始提取...")
                if not self.extract_book_features():
                    logger.error("特征提取失败，无法推荐")
                    return []

            # 2. 获取用户评分历史
            user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]

            if user_ratings.empty:
                logger.warning(f"用户 {user_id} 没有评分历史，无法构建内容画像")
                return []

            logger.info(f"用户 {user_id} 评分了 {len(user_ratings)} 本图书")

            # 3. 构建用户TF-IDF向量（加权平均）
            user_vector = self._build_user_tfidf_vector(user_id, user_ratings)

            if user_vector is None:
                logger.error("用户向量构建失败")
                return []

            # 4. 获取候选图书（排除已评分）
            rated_book_ids = set(user_ratings['book_id'].values)
            candidate_mask = ~self.books_df['book_id'].isin(rated_book_ids)
            candidate_indices = self.books_df[candidate_mask].index.tolist()

            if not candidate_indices:
                logger.warning("没有候选图书（用户已评分所有图书）")
                return []

            logger.info(f"候选图书数量: {len(candidate_indices):,}")

            # 5. 批量计算余弦相似度（矩阵运算，速度快）
            candidate_features = self.book_features[candidate_indices]
            similarities = cosine_similarity(user_vector, candidate_features)[0]

            # 6. 排序获取Top-N
            top_indices = np.argsort(similarities)[::-1][:top_n]
            top_candidate_indices = [candidate_indices[i] for i in top_indices]
            top_similarities = similarities[top_indices]

            # 7. 构建推荐结果
            recommendations = []
            for idx, similarity in zip(top_candidate_indices, top_similarities):
                book = self.books_df.iloc[idx]
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
                    'similarity': round(float(similarity), 3),
                    'algorithm': 'content_based_tfidf',
                    'reason': f'内容相似度{similarity:.2f}，与您的阅读偏好匹配'
                })

            logger.info(f"基于TF-IDF生成 {len(recommendations)} 个推荐")
            return recommendations

        except Exception as e:
            logger.error(f"TF-IDF内容推荐失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _build_user_tfidf_vector(self, user_id, user_ratings):
        """
        构建用户的TF-IDF向量（加权平均）

        原理：
        用户向量 = Σ(评分 × 图书向量) / Σ评分
        评分高的图书在用户向量中权重更大

        参数:
            user_id: 用户ID
            user_ratings: 用户评分记录

        返回:
            稀疏矩阵: 用户TF-IDF向量 (1 × 特征维度)
        """
        try:
            # 合并用户评分与图书信息，获取book_id对应的索引
            user_books = user_ratings.merge(
                self.books_df[['book_id']].reset_index(),
                on='book_id',
                how='inner'
            )

            if user_books.empty:
                logger.warning(f"用户 {user_id} 的评分图书在books_df中找不到")
                return None

            # 提取图书索引和评分权重
            book_indices = user_books['index'].tolist()
            weights = user_books['rating'].values

            logger.info(f"用户向量基于 {len(book_indices)} 本图书构建")

            # 提取这些图书的TF-IDF向量
            user_rated_features = self.book_features[book_indices]

            # 加权平均（评分作为权重）
            # 注意：稀疏矩阵的乘法需要特殊处理
            import scipy.sparse as sp
            weights = weights.reshape(-1, 1)
            weighted_features = user_rated_features.multiply(weights)
            user_vector = weighted_features.sum(axis=0) / weights.sum()

            # 修复：将np.matrix转换为numpy数组，避免sklearn报错
            # user_vector.sum(axis=0)返回的是np.matrix (1, n)，需要转为(1, n) numpy array
            if isinstance(user_vector, np.matrix):
                user_vector = np.asarray(user_vector)

            return user_vector

        except Exception as e:
            logger.error(f"构建用户TF-IDF向量失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
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
                similarity += 0.4
            
            # 2. 出版社相似度 (权重20%)
            if book1['publisher'] == book2['publisher'] and pd.notna(book1['publisher']):
                similarity += 0.3
            
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

    def _get_user_basic_info(self, user_id):
        """获取用户基础信息"""
        try:
            user_query = """
            SELECT user_id, age, country, age_group
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
            (user_info.get('country') is not None and str(user_info.get('country')).strip() != '')
        )
    
    def _recommend_by_user_features(self, user_info, user_id, top_n):
        """基于用户特征推荐图书"""
        try:
            recommendations = []
            
            # 获取用户已评分的图书（重要：必须排除）
            user_rated_books = set()
            if user_id:
                user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
                user_rated_books = set(user_ratings['book_id'].values)
            
            # 获取高质量图书池（排除用户已评分的）
            quality_books = self.books_df[
                (self.books_df['rating_count'] >= 5) &
                (self.books_df['avg_rating'] >= 3.5) &
                (~self.books_df['book_id'].isin(user_rated_books))  # 关键：排除已评分图书
            ].copy()
            
            logger.info(f"候选图书池: {len(quality_books)} 本（已排除用户已评分的 {len(user_rated_books)} 本）")
            
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
            
            # 1. 年龄组匹配 (权重50%)
            user_age_group = user_info.get('age_group')
            user_age = user_info.get('age')
            
            if user_age_group or user_age:
                book_year = book.get('year')
                if pd.notna(book_year):
                    # 基于年龄组的图书年代偏好
                    if user_age_group == 'Under 18' or (user_age and user_age < 18):
                        age_score = 1.0 if book_year >= 2005 else 0.6  # 青少年偏好新书
                    elif user_age_group == '18-24' or (user_age and 18 <= user_age < 25):
                        age_score = 1.0 if book_year >= 2000 else 0.7  # 年轻人偏好现代书籍
                    elif user_age_group == '25-34' or (user_age and 25 <= user_age < 35):
                        age_score = 1.0 if book_year >= 1990 else 0.8  # 青年偏好当代文学
                    elif user_age_group == '35-44' or (user_age and 35 <= user_age < 45):
                        age_score = 1.0 if book_year >= 1980 else 0.9  # 中年偏好成熟作品
                    elif user_age_group == '45-54' or (user_age and 45 <= user_age < 55):
                        age_score = 1.0 if book_year >= 1970 else 0.9  # 偏好经典文学
                    elif user_age_group == '55+' or (user_age and user_age >= 55):
                        age_score = 1.0 if book_year <= 1990 else 0.8  # 老年偏好传统经典
                    else:
                        age_score = 0.5  # 未知年龄组默认分数
                    
                    score += 0.5 * age_score
            
            # 2. 国家/文化匹配 (权重30%) - 安全的字符串处理
            try:
                user_country = user_info.get('country')
                user_country = str(user_country).lower() if user_country else ''
                
                book_title = book.get('title')
                book_title = str(book_title).lower() if book_title else ''
                
                book_author = book.get('author')  
                book_author = str(book_author).lower() if book_author else ''
                
                if user_country:
                    # 简单的文化匹配规则
                    if user_country in ['usa', 'united states', 'canada', 'uk', 'united kingdom', 'australia']:
                        # 英语国家用户偏好英语作品
                        if any(name in book_author for name in ['john', 'david', 'michael', 'james', 'robert', 'william', 'thomas']):
                            score += 0.3 * 0.8
                    elif user_country in ['germany', 'france', 'spain', 'italy', 'netherlands']:
                        # 欧洲用户偏好欧洲文学
                        if any(word in book_title for word in ['europe', 'paris', 'london', 'berlin', 'rome']):
                            score += 0.3 * 0.8
                    else:
                        # 其他国家用户偏好国际经典
                        score += 0.3 * 0.5
            except Exception as e:
                # 字符串处理失败，跳过文化匹配
                pass
            
            # 3. 图书质量评分 (权重20%)
            try:
                avg_rating = book.get('avg_rating') or 0
                rating_count = book.get('rating_count') or 0
                
                quality_score = float(avg_rating) / 5.0
                popularity_score = min(1.0, int(rating_count) / 100)
                combined_quality = (quality_score + popularity_score) / 2
                score += 0.2 * combined_quality
            except Exception as e:
                # 质量评分计算失败，跳过
                pass
            
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
    
    def _get_top_quality_books_excluding_rated(self, user_id, top_n):
        """获取优质图书推荐（排除用户已评分的）"""
        logger.info("返回评分最高且评价人数最多的热门图书（排除已评分）")
        
        try:
            # 获取用户已评分的图书
            user_rated_books = set()
            if user_id:
                user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
                user_rated_books = set(user_ratings['book_id'].values)
            
            # 选择评分高且评分人数多的图书（排除已评分）
            top_books = self.books_df[
                (self.books_df['rating_count'] >= 20) &  # 至少20人评分
                (self.books_df['avg_rating'] >= 4.0) &   # 评分4.0以上
                (~self.books_df['book_id'].isin(user_rated_books))  # 排除已评分
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
                    'algorithm': 'top_quality_books_filtered',
                    'reason': f'高质量热门图书（{book["avg_rating"]:.1f}分，{book["rating_count"]}人评价）'
                })
            
            return recommendations

        except Exception as e:
            logger.error(f"获取热门优质图书失败: {e}")
            return []

    def _get_top_quality_books(self, top_n):
        """获取优质热门图书（不排除已评分，用于fallback场景）"""
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