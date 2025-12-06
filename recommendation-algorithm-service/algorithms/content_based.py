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
        """
        基于TF-IDF向量的相似图书推荐（与个人推荐页面技术统一）

        原理：
        1. 提取目标图书的TF-IDF向量
        2. 预筛选候选图书（性能优化）
        3. 批量计算TF-IDF余弦相似度
        4. 返回相似度最高的Top-K图书

        参数:
            target_book_id: 目标图书ID
            top_k: 返回数量

        返回:
            list: 相似图书列表
        """
        logger.info(f"[TF-IDF方法] 查找与图书 {target_book_id} 相似的图书...")

        try:
            # 0. 确保TF-IDF特征矩阵已提取
            if self.book_features is None:
                logger.warning("TF-IDF特征矩阵未提取，开始提取...")
                if not self.extract_book_features():
                    logger.error("TF-IDF特征提取失败，降级到属性匹配方法")
                    return self._get_similar_books_by_content_fallback(target_book_id, top_k)

            # 1. 获取目标图书信息和索引
            target_book = self.books_df[self.books_df['book_id'] == target_book_id]
            if target_book.empty:
                logger.warning(f"图书 {target_book_id} 不存在")
                return []

            target_book_idx = target_book.index[0]
            target_book_data = target_book.iloc[0]
            logger.info(f"目标图书: {target_book_data['title']} - {target_book_data['author']}")

            # 2. 提取目标图书的TF-IDF向量
            target_vector = self.book_features[target_book_idx]

            # 3. 预筛选候选图书（避免与14万本图书全量比较）
            candidate_books = self._get_content_candidates(target_book_data)
            logger.info(f"预筛选候选图书: {len(candidate_books)} 本（从{len(self.books_df):,}本筛选）")

            if len(candidate_books) == 0:
                logger.warning("没有找到合适的候选图书")
                return []

            # 4. 获取候选图书的索引
            candidate_indices = candidate_books.index.tolist()

            # 5. 批量计算TF-IDF余弦相似度（矩阵运算，高效）
            candidate_features = self.book_features[candidate_indices]
            similarities = cosine_similarity(target_vector, candidate_features)[0]

            # 6. 排序获取Top-K
            top_indices = np.argsort(similarities)[::-1][:top_k]
            top_similarities = similarities[top_indices]

            # 7. 构建推荐结果
            recommendations = []
            for idx, similarity in zip(top_indices, top_similarities):
                book = candidate_books.iloc[idx]
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
                    'content_score': round(float(similarity), 3),
                    'algorithm': 'content_based_tfidf',
                    'reason': f'TF-IDF内容相似度{similarity:.2f}'
                })

            logger.info(f"[TF-IDF方法] 找到 {len(recommendations)} 本相似图书（平均相似度: {np.mean(top_similarities):.3f}）")
            return recommendations

        except Exception as e:
            logger.error(f"TF-IDF相似图书推荐失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # 降级到属性匹配方法
            return self._get_similar_books_by_content_fallback(target_book_id, top_k)

    def _get_similar_books_by_content_fallback(self, target_book_id, top_k=10):
        """
        降级方案：基于简单属性匹配的相似图书推荐
        （当TF-IDF特征矩阵不可用时使用）
        """
        logger.warning("使用降级方案：简单属性匹配")

        try:
            # 获取目标图书信息
            target_book = self.books_df[self.books_df['book_id'] == target_book_id]
            if target_book.empty:
                return []

            target_book_data = target_book.iloc[0]

            # 预筛选候选图书
            candidate_books = self._get_content_candidates(target_book_data)

            if len(candidate_books) == 0:
                return []

            # 计算属性相似度
            similarities = []

            for _, book in candidate_books.iterrows():
                if book['book_id'] == target_book_id:
                    continue

                # 使用属性匹配计算相似度
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
                        'content_score': round(similarity, 3),
                        'algorithm': 'content_based_attributes',
                        'reason': f'属性相似度{similarity:.2f}'
                    })

            # 按相似度排序
            similarities.sort(key=lambda x: x['similarity'], reverse=True)

            logger.info(f"[属性匹配] 找到 {len(similarities[:top_k])} 本相似图书")
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"属性匹配相似图书推荐失败: {e}")
            return []
    
    def _get_content_candidates(self, target_book):
        """预筛选候选图书（性能优化关键）"""
        try:
            candidate_books = pd.DataFrame()
            # 使用集合追踪已添加的book_id，避免访问空DataFrame的列
            added_book_ids = set()

            # 1. 同主题图书（新增：最高优先级）
            if pd.notna(target_book.get('theme_id')):
                same_theme = self.books_df[
                    (self.books_df['theme_id'] == target_book['theme_id']) &
                    (self.books_df['book_id'] != target_book['book_id'])
                ]
                candidate_books = pd.concat([candidate_books, same_theme], ignore_index=True)
                added_book_ids.update(same_theme['book_id'].values)
                logger.info(f"找到同主题图书: {len(same_theme)} 本")

            # 2. 同作者图书
            if pd.notna(target_book['author']):
                same_author = self.books_df[
                    (self.books_df['author'] == target_book['author']) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(added_book_ids))  # 去重
                ]
                candidate_books = pd.concat([candidate_books, same_author], ignore_index=True)
                added_book_ids.update(same_author['book_id'].values)
                logger.info(f"找到同作者图书: {len(same_author)} 本")

            # 3. 同出版社图书
            if pd.notna(target_book['publisher']):
                same_publisher = self.books_df[
                    (self.books_df['publisher'] == target_book['publisher']) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(added_book_ids))  # 去重
                ]
                candidate_books = pd.concat([candidate_books, same_publisher], ignore_index=True)
                added_book_ids.update(same_publisher['book_id'].values)
                logger.info(f"找到同出版社图书: {len(same_publisher)} 本")

            # 4. 相近年代图书（±10年）
            if pd.notna(target_book['year']):
                target_year = int(target_book['year'])
                nearby_years = self.books_df[
                    (self.books_df['year'] >= target_year - 10) &
                    (self.books_df['year'] <= target_year + 10) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(added_book_ids))  # 去重
                ]
                # 限制相近年代的数量，避免过多
                nearby_years_sample = nearby_years.nlargest(500, ['avg_rating', 'rating_count'])
                candidate_books = pd.concat([candidate_books, nearby_years_sample], ignore_index=True)
                added_book_ids.update(nearby_years_sample['book_id'].values)
                logger.info(f"找到相近年代图书: {len(nearby_years_sample)} 本")

            # 5. 高质量图书补充（如果候选不够）
            if len(candidate_books) < 100:
                quality_books = self.books_df[
                    (self.books_df['avg_rating'] >= 4.0) &
                    (self.books_df['rating_count'] >= 20) &
                    (self.books_df['book_id'] != target_book['book_id']) &
                    (~self.books_df['book_id'].isin(added_book_ids))  # 去重
                ].head(200)  # 限制数量
                candidate_books = pd.concat([candidate_books, quality_books], ignore_index=True)
                logger.info(f"补充高质量图书: {len(quality_books)} 本")

            # 去重并限制最终候选数量
            candidate_books = candidate_books.drop_duplicates(subset=['book_id']).head(1000)

            logger.info(f"最终候选图书数量: {len(candidate_books)} 本")
            return candidate_books

        except Exception as e:
            logger.error(f"预筛选候选图书失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def _calculate_book_content_similarity(self, book1, book2):
        """
        计算两本图书的内容相似度（增强版：包含主题匹配）

        权重分配（总计1.0）：
        - 作者相似度: 0.30 (30%)
        - 主题相似度: 0.25 (25%) ← 新增
        - 出版社相似度: 0.25 (25%)
        - 年份相似度: 0.15 (15%)
        - 评分相似度: 0.05 (5%)
        """
        try:
            similarity = 0.0

            # 1. 作者相似度 (权重30%)
            if book1['author'] == book2['author'] and pd.notna(book1['author']):
                similarity += 0.30

            # 2. 主题相似度 (权重25%) ← 新增
            if pd.notna(book1.get('theme_id')) and pd.notna(book2.get('theme_id')):
                if book1['theme_id'] == book2['theme_id']:
                    similarity += 0.25

            # 3. 出版社相似度 (权重25%)
            if book1['publisher'] == book2['publisher'] and pd.notna(book1['publisher']):
                similarity += 0.25

            # 4. 年份相似度 (权重15%)
            if pd.notna(book1['year']) and pd.notna(book2['year']):
                year_diff = abs(int(book1['year']) - int(book2['year']))
                year_similarity = max(0, 1 - year_diff / 20)  # 20年内认为相似
                similarity += 0.15 * year_similarity

            # 5. 评分相似度 (权重5%)
            if pd.notna(book1['avg_rating']) and pd.notna(book2['avg_rating']):
                rating_diff = abs(float(book1['avg_rating']) - float(book2['avg_rating']))
                rating_similarity = max(0, 1 - rating_diff / 2)  # 2分内认为相似
                similarity += 0.05 * rating_similarity

            return similarity

        except Exception as e:
            logger.error(f"计算图书内容相似度失败: {e}")
            return 0.0

    def _get_user_basic_info(self, user_id):
        """
        获取用户基础信息（年龄 + 兴趣）

        返回:
            dict: {
                'user_id': int,
                'age': int or None,
                'age_group': str or None,
                'interests': list[int]  # 兴趣主题ID列表
            }
        """
        try:
            # 获取用户基本信息
            user_query = """
            SELECT user_id, age, age_group
            FROM users
            WHERE user_id = %(user_id)s
            """

            user_df = pd.read_sql(user_query, self.data_loader.engine, params={'user_id': user_id})

            if user_df.empty:
                return None

            user_info = user_df.iloc[0].to_dict()

            # 获取用户兴趣列表
            user_info['interests'] = self.data_loader.get_user_interests(user_id)

            return user_info

        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None

    def _has_valid_user_features(self, user_info):
        """
        检查用户是否有有效的特征信息（年龄或兴趣）

        优先级：兴趣 > 年龄（用户主动选择的偏好更重要）
        """
        if not user_info:
            return False

        has_age = user_info.get('age') is not None and user_info.get('age') > 0
        has_interests = bool(user_info.get('interests'))

        return has_age or has_interests

    def has_user_interests(self, user_info):
        """检查用户是否选择了兴趣"""
        return bool(user_info and user_info.get('interests'))
    
    def _recommend_by_user_features(self, user_info, user_id, top_n):
        """
        基于用户特征推荐图书

        优先级策略（方案A）：
        1. 兴趣优先：如果用户选择了兴趣，优先推荐兴趣主题的图书
        2. 年龄辅助：如果用户有年龄信息，作为辅助排序条件
        3. 质量兜底：如果兴趣推荐不足，用高质量图书补充
        """
        try:
            # 获取用户已评分的图书（必须排除）
            user_rated_books = set()
            if user_id:
                user_ratings = self.ratings_df[self.ratings_df['user_id'] == user_id]
                user_rated_books = set(user_ratings['book_id'].values)

            logger.info(f"用户 {user_id} 已评分图书: {len(user_rated_books)} 本")

            # 检查是否有兴趣
            user_interests = user_info.get('interests', [])

            if user_interests:
                # 优先使用兴趣推荐
                logger.info(f"用户选择了 {len(user_interests)} 个兴趣主题，使用兴趣推荐")
                recommendations = self._recommend_by_interests(
                    user_id, user_interests, user_rated_books, user_info, top_n
                )

                if len(recommendations) >= top_n:
                    return recommendations[:top_n]

                # 兴趣推荐不足，用年龄偏好补充
                logger.info(f"兴趣推荐 {len(recommendations)} 个，不足 {top_n}，尝试年龄偏好补充")
                if user_info.get('age'):
                    age_recs = self._recommend_by_age(user_id, user_info, user_rated_books, top_n - len(recommendations))
                    # 去重
                    existing_ids = {r['bookId'] for r in recommendations}
                    for rec in age_recs:
                        if rec['bookId'] not in existing_ids:
                            recommendations.append(rec)
                            if len(recommendations) >= top_n:
                                break

                return recommendations[:top_n]

            elif user_info.get('age'):
                # 只有年龄，使用年龄偏好推荐
                logger.info("用户只有年龄信息，使用年龄偏好推荐")
                return self._recommend_by_age(user_id, user_info, user_rated_books, top_n)

            else:
                # 无特征，返回高质量图书
                logger.info("用户无有效特征，返回高质量图书")
                return self._get_top_quality_books_excluding_rated(user_id, top_n)

        except Exception as e:
            logger.error(f"基于用户特征推荐失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_top_quality_books(top_n)

    def _recommend_by_interests(self, user_id, interest_ids, exclude_book_ids, user_info, top_n):
        """
        基于用户兴趣主题推荐图书

        核心逻辑：
        1. 根据 user_interests 中的 theme_id 匹配 books 表的 theme_id
        2. 按评分和评分人数排序
        3. 排除用户已评分的图书
        """
        logger.info(f"基于兴趣推荐: 兴趣主题ID = {interest_ids}")

        try:
            # 使用 data_loader 获取符合主题的图书
            interest_books = self.data_loader.get_books_by_themes(
                theme_ids=interest_ids,
                exclude_book_ids=exclude_book_ids,
                limit=top_n * 2
            )

            if interest_books.empty:
                logger.warning("未找到符合用户兴趣的图书")
                return []

            logger.info(f"找到 {len(interest_books)} 本符合兴趣的图书")

            # 构建推荐结果
            recommendations = []
            user_age = user_info.get('age')

            for _, book in interest_books.iterrows():
                # 计算匹配分数（兴趣匹配 + 年龄偏好加成）
                match_score = 0.7  # 兴趣基础分

                # 年龄偏好加成
                if user_age and pd.notna(book.get('year')):
                    age_bonus = self._calculate_age_preference_score(user_age, book['year'])
                    match_score += 0.3 * age_bonus

                recommendations.append({
                    'bookId': book['book_id'],
                    'title': book['title'],
                    'author': book['author'] or '未知作者',
                    'publisher': book.get('publisher', '') or '',
                    'year': int(book['year']) if pd.notna(book.get('year')) else None,
                    'imageUrlS': book.get('image_url_s', ''),
                    'imageUrlM': book.get('image_url_m', ''),
                    'imageUrlL': book.get('image_url_l', ''),
                    'avgRating': round(float(book['avg_rating']), 2),
                    'ratingCount': int(book['rating_count']),
                    'content_score': round(match_score, 3),
                    'algorithm': 'interest_based',
                    'reason': '根据您选择的兴趣主题推荐'
                })

            # 按匹配分数排序
            recommendations.sort(key=lambda x: (x['content_score'], x['avgRating']), reverse=True)

            logger.info(f"兴趣推荐生成 {len(recommendations[:top_n])} 个结果")
            return recommendations[:top_n]

        except Exception as e:
            logger.error(f"基于兴趣推荐失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _recommend_by_age(self, user_id, user_info, exclude_book_ids, top_n):
        """
        基于用户年龄偏好推荐图书

        年龄偏好规则：
        - 青少年(<18): 偏好2005年后的新书
        - 年轻人(18-24): 偏好2000年后的现代书籍
        - 青年(25-34): 偏好1990年后的当代文学
        - 中年(35-44): 偏好1980年后的成熟作品
        - 中老年(45-54): 偏好经典文学
        - 老年(55+): 偏好传统经典
        """
        logger.info(f"基于年龄推荐: 年龄 = {user_info.get('age')}")

        try:
            user_age = user_info.get('age')

            # 获取高质量图书池
            quality_books = self.books_df[
                (self.books_df['rating_count'] >= 5) &
                (self.books_df['avg_rating'] >= 3.5) &
                (~self.books_df['book_id'].isin(exclude_book_ids))
            ].copy()

            if quality_books.empty:
                return []

            # 计算年龄偏好分数
            recommendations = []

            for _, book in quality_books.iterrows():
                if pd.notna(book.get('year')):
                    age_score = self._calculate_age_preference_score(user_age, book['year'])
                else:
                    age_score = 0.5  # 无年份信息默认分数

                # 综合评分 = 年龄偏好 * 0.5 + 图书质量 * 0.5
                quality_score = (float(book['avg_rating']) / 5.0 + min(1.0, book['rating_count'] / 100)) / 2
                match_score = 0.5 * age_score + 0.5 * quality_score

                if match_score > 0.3:
                    recommendations.append({
                        'bookId': book['book_id'],
                        'title': book['title'],
                        'author': book['author'] or '未知作者',
                        'publisher': book.get('publisher', '') or '',
                        'year': int(book['year']) if pd.notna(book.get('year')) else None,
                        'imageUrlS': book.get('image_url_s', ''),
                        'imageUrlM': book.get('image_url_m', ''),
                        'imageUrlL': book.get('image_url_l', ''),
                        'avgRating': round(float(book['avg_rating']), 2),
                        'ratingCount': int(book['rating_count']),
                        'content_score': round(match_score, 3),
                        'algorithm': 'age_based',
                        'reason': self._get_age_recommendation_reason(user_age)
                    })

            # 按匹配分数排序
            recommendations.sort(key=lambda x: x['content_score'], reverse=True)

            return recommendations[:top_n]

        except Exception as e:
            logger.error(f"基于年龄推荐失败: {e}")
            return []

    def _calculate_age_preference_score(self, user_age, book_year):
        """计算用户年龄与图书年代的匹配分数"""
        try:
            book_year = int(book_year)

            if user_age < 18:
                return 1.0 if book_year >= 2005 else 0.6
            elif 18 <= user_age < 25:
                return 1.0 if book_year >= 2000 else 0.7
            elif 25 <= user_age < 35:
                return 1.0 if book_year >= 1990 else 0.8
            elif 35 <= user_age < 45:
                return 1.0 if book_year >= 1980 else 0.9
            elif 45 <= user_age < 55:
                return 1.0 if book_year >= 1970 else 0.9
            else:  # 55+
                return 1.0 if book_year <= 1990 else 0.8

        except (ValueError, TypeError):
            return 0.5

    def _get_age_recommendation_reason(self, user_age):
        """根据年龄生成推荐理由"""
        if user_age < 18:
            return "适合青少年读者的新书推荐"
        elif 18 <= user_age < 25:
            return "适合年轻读者的现代书籍"
        elif 25 <= user_age < 35:
            return "适合青年读者的当代文学"
        elif 35 <= user_age < 45:
            return "适合成熟读者的优质作品"
        elif 45 <= user_age < 55:
            return "经典文学推荐"
        else:
            return "传统经典作品推荐"
    
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
            'name': '基于TF-IDF内容特征的推荐',
            'type': 'content_based_filtering',
            'description': '基于TF-IDF文本向量和图书内容特征的相似性推荐，解决冷启动问题',
            'features': [
                'TF-IDF文本特征（1500维）',
                '标题+作者+出版社组合向量',
                '年份标准化特征',
                '评分质量特征',
                '主题分类匹配',
                '属性匹配降级方案'
            ],
            'advantages': [
                '语义相似性捕捉（TF-IDF）',
                '无冷启动问题',
                '推荐解释性强',
                '不依赖用户行为',
                '降级机制保证鲁棒性'
            ]
        }