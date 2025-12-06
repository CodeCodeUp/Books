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

        # 提取图书TF-IDF特征矩阵（启动时预计算）
        logger.info("开始提取图书TF-IDF特征矩阵...")
        if self.content_cf.extract_book_features():
            logger.info("混合推荐算法 - TF-IDF特征矩阵提取成功")
        else:
            logger.error("混合推荐算法 - TF-IDF特征矩阵提取失败")

        logger.info("混合推荐算法 - 数据加载完成")
    
    def get_hybrid_user_recommendations(self, user_id, top_n=10, cf_ratio=0.7):
        """
        混合推荐：用户协同过滤 + 内容特征 (推荐页面使用)

        【重要更新】现已支持动态比例调节！
        - cf_ratio 参数已弃用，系统将根据协同过滤置信度自动计算最优混合比例
        - 动态比例范围：协同过滤 50%-90%，内容特征 10%-50%
        - 置信度计算：基于相似用户数量和平均相似度

        参数:
            user_id: 用户ID
            top_n: 推荐数量
            cf_ratio: (已弃用) 保留用于API兼容性，实际使用动态计算

        返回:
            list: 推荐列表，每个推荐包含置信度信息
        """
        logger.info(f"为用户 {user_id} 生成动态比例混合推荐 (协同过滤比例将自动计算)")

        try:
            # 1. 检查用户是否有评分历史
            user_ratings = self.user_cf.ratings_df[self.user_cf.ratings_df['user_id'] == user_id]
            has_ratings = not user_ratings.empty

            # 2. 检查用户是否有基础特征信息（年龄或兴趣）
            user_info = self.content_cf._get_user_basic_info(user_id)
            has_features = user_info and self.content_cf._has_valid_user_features(user_info)

            # 详细记录用户特征状态
            if user_info:
                has_interests = bool(user_info.get('interests'))
                has_age = user_info.get('age') is not None and user_info.get('age') > 0
                logger.info(f"用户状态: 有评分历史={has_ratings}, 有兴趣={has_interests}, 有年龄={has_age}")
            else:
                logger.info(f"用户状态: 有评分历史={has_ratings}, 无用户信息")

            # 3. 根据用户状态决定推荐策略
            if has_ratings and has_features:
                # 情况1: 既有评分又有特征 - 检查是否有兴趣
                has_interests = bool(user_info.get('interests'))

                if has_interests:
                    # 有兴趣：使用三层混合推荐（CF + TF-IDF + 兴趣加权）
                    logger.info("用户有评分历史和兴趣，使用三层混合推荐（CF + TF-IDF + 兴趣加权）")
                    return self._get_triple_hybrid_recommendations(user_id, user_info, top_n)
                else:
                    # 只有年龄：使用双层混合推荐（CF + TF-IDF）
                    logger.info("用户有评分历史和年龄（无兴趣），使用双层混合推荐（CF + TF-IDF）")
                    return self._get_dual_hybrid_recommendations(user_id, top_n)

            elif has_ratings:
                # 情况2: 有评分无特征 - 协同过滤 + TF-IDF内容特征混合
                logger.info("用户有评分历史但无特征信息（年龄/兴趣），使用协同过滤 + TF-IDF内容特征混合")

                cf_recommendations, similar_users, user_rating_count = self._get_cf_recommendations_no_fallback(user_id, top_n * 2)
                logger.info(f"协同过滤结果: {len(cf_recommendations)} 个推荐")

                # 使用TF-IDF内容特征推荐（基于评分历史，不需要用户特征）
                content_recommendations = self.content_cf.get_content_based_recommendations(user_id, top_n * 2)
                logger.info(f"TF-IDF内容特征结果: {len(content_recommendations)} 个推荐")

                if cf_recommendations and content_recommendations:
                    # 动态计算混合比例
                    dynamic_cf_ratio, dynamic_content_ratio, confidence_info = self._calculate_dynamic_cf_ratio(
                        similar_users, user_rating_count
                    )

                    logger.info(
                        f"[动态混合推荐] "
                        f"协同过滤={dynamic_cf_ratio:.1%}, "
                        f"内容特征={dynamic_content_ratio:.1%} | "
                        f"置信度={confidence_info.get('confidence_score', 'N/A')}"
                    )

                    # 混合推荐
                    mixed_result = self._mix_recommendations(
                        cf_recommendations,
                        content_recommendations,
                        dynamic_cf_ratio,
                        top_n
                    )

                    for rec in mixed_result:
                        rec['mixing_strategy'] = 'dynamic_confidence_based'
                        rec['cf_ratio'] = round(dynamic_cf_ratio, 2)
                        rec['confidence_score'] = confidence_info.get('confidence_score')

                    logger.info(f"动态混合推荐完成: {len(mixed_result)} 个推荐")
                    return mixed_result
                elif cf_recommendations:
                    return cf_recommendations[:top_n]
                elif content_recommendations:
                    return content_recommendations[:top_n]
                else:
                    logger.warning("协同过滤和内容特征都无结果，使用降级推荐")
                    fallback_result = self._get_fallback_recommendations(top_n)
                    logger.info(f"降级推荐: {len(fallback_result)} 个推荐")
                    return fallback_result

            elif has_features:
                # 情况3: 有特征无评分 - 基于用户特征推荐（兴趣优先，年龄辅助）
                logger.info("用户有特征信息（年龄/兴趣）但无评分历史，使用基于特征的推荐")
                content_result = self.content_cf._recommend_by_user_features(user_info, user_id, top_n)
                logger.info(f"基于用户特征推荐: {len(content_result)} 个推荐")
                return content_result

            else:
                # 情况4: 既无评分又无特征 - 优质热门图书
                logger.info("用户既无评分历史又无特征信息（年龄/兴趣），返回优质热门图书")
                fallback_result = self._get_fallback_recommendations(top_n)
                logger.info(f"优质热门图书推荐: {len(fallback_result)} 个推荐")
                return fallback_result

        except Exception as e:
            logger.error(f"混合推荐失败: {e}")
            return self._get_fallback_recommendations(top_n)

    def _get_triple_hybrid_recommendations(self, user_id, user_info, top_n):
        """
        三层混合推荐：CF + TF-IDF + 兴趣加权

        核心思想：
        1. 获取协同过滤推荐（CF）
        2. 获取TF-IDF内容推荐（Content）
        3. 获取兴趣主题推荐（Interest）
        4. 对兴趣主题匹配的图书进行加权提升
        5. 按动态比例混合三种推荐源

        参数:
            user_id: 用户ID
            user_info: 用户信息（包含兴趣列表）
            top_n: 推荐数量

        返回:
            list: 混合推荐结果
        """
        try:
            # 1. 获取协同过滤推荐
            cf_recommendations, similar_users, user_rating_count = self._get_cf_recommendations_no_fallback(user_id, top_n * 2)
            logger.info(f"协同过滤结果: {len(cf_recommendations)} 个推荐")

            # 2. 获取TF-IDF内容特征推荐
            content_recommendations = self.content_cf.get_content_based_recommendations(user_id, top_n * 2)
            logger.info(f"TF-IDF内容特征结果: {len(content_recommendations)} 个推荐")

            # 3. 获取用户兴趣主题ID
            user_interests = user_info.get('interests', [])
            logger.info(f"用户兴趣主题: {user_interests}")

            if not cf_recommendations and not content_recommendations:
                logger.warning("协同过滤和TF-IDF都无结果，降级到兴趣推荐")
                return self.content_cf._recommend_by_user_features(user_info, user_id, top_n)

            # 4. 动态计算CF和Content的基础比例
            dynamic_cf_ratio, dynamic_content_ratio, confidence_info = self._calculate_dynamic_cf_ratio(
                similar_users, user_rating_count
            )

            logger.info(
                f"[三层混合] 基础比例 - "
                f"协同过滤={dynamic_cf_ratio:.1%}, "
                f"内容特征={dynamic_content_ratio:.1%}, "
                f"置信度={confidence_info.get('confidence_score', 'N/A')}"
            )

            # 5. 对推荐结果进行兴趣加权
            cf_with_interest_boost = self._apply_interest_boost(cf_recommendations, user_interests)
            content_with_interest_boost = self._apply_interest_boost(content_recommendations, user_interests)

            # 6. 按动态比例混合
            mixed_result = self._mix_recommendations(
                cf_with_interest_boost,
                content_with_interest_boost,
                dynamic_cf_ratio,
                top_n
            )

            # 7. 添加元数据
            for rec in mixed_result:
                rec['mixing_strategy'] = 'triple_hybrid_with_interest_boost'
                rec['cf_ratio'] = round(dynamic_cf_ratio, 2)
                rec['confidence_score'] = confidence_info.get('confidence_score')
                rec['interest_boosted'] = rec.get('interest_boosted', False)

            logger.info(f"三层混合推荐完成: {len(mixed_result)} 个推荐")
            return mixed_result

        except Exception as e:
            logger.error(f"三层混合推荐失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_fallback_recommendations(top_n)

    def _get_dual_hybrid_recommendations(self, user_id, top_n):
        """
        双层混合推荐：CF + TF-IDF（无兴趣加权）

        适用场景：用户有评分历史和年龄，但没有选择兴趣

        参数:
            user_id: 用户ID
            top_n: 推荐数量

        返回:
            list: 混合推荐结果
        """
        try:
            # 1. 获取协同过滤推荐
            cf_recommendations, similar_users, user_rating_count = self._get_cf_recommendations_no_fallback(user_id, top_n * 2)
            logger.info(f"协同过滤结果: {len(cf_recommendations)} 个推荐")

            # 2. 获取TF-IDF内容特征推荐
            content_recommendations = self.content_cf.get_content_based_recommendations(user_id, top_n * 2)
            logger.info(f"TF-IDF内容特征结果: {len(content_recommendations)} 个推荐")

            if not cf_recommendations and not content_recommendations:
                logger.warning("两种算法都无结果，使用降级推荐")
                return self._get_fallback_recommendations(top_n)

            # 3. 动态计算混合比例
            dynamic_cf_ratio, dynamic_content_ratio, confidence_info = self._calculate_dynamic_cf_ratio(
                similar_users, user_rating_count
            )

            logger.info(
                f"[双层混合] "
                f"协同过滤={dynamic_cf_ratio:.1%}, "
                f"内容特征={dynamic_content_ratio:.1%} | "
                f"置信度={confidence_info.get('confidence_score', 'N/A')}"
            )

            # 4. 混合推荐
            if cf_recommendations and content_recommendations:
                mixed_result = self._mix_recommendations(
                    cf_recommendations,
                    content_recommendations,
                    dynamic_cf_ratio,
                    top_n
                )
            elif cf_recommendations:
                mixed_result = cf_recommendations[:top_n]
            else:
                mixed_result = content_recommendations[:top_n]

            # 5. 添加元数据
            for rec in mixed_result:
                rec['mixing_strategy'] = 'dual_hybrid_cf_tfidf'
                rec['cf_ratio'] = round(dynamic_cf_ratio, 2)
                rec['confidence_score'] = confidence_info.get('confidence_score')

            logger.info(f"双层混合推荐完成: {len(mixed_result)} 个推荐")
            return mixed_result

        except Exception as e:
            logger.error(f"双层混合推荐失败: {e}")
            return self._get_fallback_recommendations(top_n)

    def _apply_interest_boost(self, recommendations, interest_theme_ids):
        """
        对符合用户兴趣主题的图书进行加权提升

        加权策略：
        - 如果图书的 theme_id 在用户兴趣列表中，提升其评分
        - 提升方式：在排序时优先级提高

        参数:
            recommendations: 推荐列表
            interest_theme_ids: 用户兴趣主题ID列表

        返回:
            list: 加权后的推荐列表（按新分数排序）
        """
        if not interest_theme_ids or not recommendations:
            return recommendations

        try:
            # 需要查询每个推荐图书的 theme_id
            boosted_recs = []

            for rec in recommendations:
                book_id = rec['bookId']

                # 查询图书的 theme_id
                book_info = self.content_cf.books_df[self.content_cf.books_df['book_id'] == book_id]

                if not book_info.empty:
                    theme_id = book_info.iloc[0].get('theme_id')

                    # 如果图书主题在用户兴趣中，进行加权
                    if pd.notna(theme_id) and int(theme_id) in interest_theme_ids:
                        # 提升评分（根据原有评分类型）
                        if 'similarity' in rec:
                            rec['similarity'] = min(1.0, rec['similarity'] * 1.3)  # 提升30%
                        if 'content_score' in rec:
                            rec['content_score'] = min(1.0, rec['content_score'] * 1.3)
                        if 'predicted_rating' in rec:
                            rec['predicted_rating'] = min(5.0, rec['predicted_rating'] * 1.15)  # 提升15%

                        rec['interest_boosted'] = True
                        rec['matched_theme_id'] = int(theme_id)
                        logger.debug(f"图书 {book_id} 匹配兴趣主题 {theme_id}，评分提升")
                    else:
                        rec['interest_boosted'] = False

                boosted_recs.append(rec)

            # 重新排序（根据提升后的评分）
            if boosted_recs:
                # 根据不同算法的评分字段排序
                if 'similarity' in boosted_recs[0]:
                    boosted_recs.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                elif 'content_score' in boosted_recs[0]:
                    boosted_recs.sort(key=lambda x: x.get('content_score', 0), reverse=True)
                elif 'predicted_rating' in boosted_recs[0]:
                    boosted_recs.sort(key=lambda x: x.get('predicted_rating', 0), reverse=True)

            interest_matched_count = sum(1 for r in boosted_recs if r.get('interest_boosted'))
            logger.info(f"兴趣加权完成: {interest_matched_count}/{len(boosted_recs)} 本图书匹配用户兴趣")

            return boosted_recs

        except Exception as e:
            logger.error(f"兴趣加权失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return recommendations

    def _get_cf_recommendations_no_fallback(self, user_id, top_n):
        """
        获取协同过滤推荐，不使用热门降级

        返回:
            tuple: (recommendations, similar_users, user_rating_count)
                - recommendations: 推荐列表
                - similar_users: 相似用户数据（用于动态比例计算）
                - user_rating_count: 用户评分数量
        """
        logger.info(f"尝试为用户 {user_id} 获取协同过滤推荐...")

        try:
            # 检查用户是否在评分矩阵中
            user_ratings = self.user_cf.ratings_df[self.user_cf.ratings_df['user_id'] == user_id]
            if user_ratings.empty:
                logger.warning(f"用户 {user_id} 在协同过滤数据中没有评分记录")
                return [], [], 0

            user_rating_count = len(user_ratings)
            logger.info(f"用户 {user_id} 有 {user_rating_count} 条评分记录")

            # 尝试找相似用户
            similar_users = self.user_cf.find_similar_users_efficient(user_id)
            if not similar_users:
                logger.warning(f"用户 {user_id} 没有找到相似用户（可能评分太少或无共同兴趣）")
                return [], [], user_rating_count

            logger.info(f"找到 {len(similar_users)} 个相似用户")

            # 生成协同过滤推荐
            recommendations = self.user_cf._generate_recommendations_efficient(user_id, similar_users, top_n, 3.0)
            logger.info(f"协同过滤生成了 {len(recommendations)} 个推荐")

            # 返回推荐列表、相似用户数据和评分数量（用于动态比例计算）
            return recommendations, similar_users, user_rating_count

        except Exception as e:
            logger.error(f"获取协同过滤推荐失败: {e}")
            return [], [], 0
    
    def _calculate_dynamic_cf_ratio(self, similar_users_data, user_rating_count):
        """
        基于协同过滤置信度动态计算混合比例

        核心思想：协同过滤的可靠性越高，其在混合推荐中的权重就越大

        参数:
            similar_users_data: list[dict] - 相似用户列表 [{'user_id': x, 'similarity': y}, ...]
            user_rating_count: int - 目标用户的评分数量

        返回:
            tuple: (cf_ratio, content_ratio, confidence_info)
                - cf_ratio: 协同过滤占比 [0.5, 0.9]
                - content_ratio: 内容特征占比 [0.1, 0.5]
                - confidence_info: 置信度详细信息（用于日志和论文分析）

        置信度计算公式:
            confidence = (相似用户数量/50) × 平均相似度
            cf_ratio = 0.5 + 0.4 × confidence  # 映射到[0.5, 0.9]区间
        """
        try:
            if not similar_users_data or len(similar_users_data) == 0:
                # 没有相似用户，返回最低协同过滤比例
                logger.warning("没有相似用户数据，使用最低协同过滤比例 (50%)")
                return 0.50, 0.50, {
                    'confidence_score': 0.0,
                    'num_similar_users': 0,
                    'avg_similarity': 0.0,
                    'user_rating_count': user_rating_count,
                    'strategy': 'minimum_cf_ratio'
                }

            # 1. 相似用户数量归一化 [0, 1]
            # 设定50个相似用户为满分，超过50个也按1.0计算
            num_similar_users = len(similar_users_data)
            user_quantity_score = min(num_similar_users / 50.0, 1.0)

            # 2. 平均相似度 [0, 1]
            similarities = [user['similarity'] for user in similar_users_data]
            avg_similarity = np.mean(similarities)

            # 3. 置信度分数 = 数量得分 × 相似度质量
            # 这个公式体现了"数量"和"质量"的双重考量
            confidence_score = user_quantity_score * avg_similarity

            # 4. 映射到协同过滤比例
            # 基准线：50%（confidence=0时）
            # 最大值：90%（confidence=1时）
            # 这样可以保证即使置信度很低，协同过滤也有一半的权重
            cf_ratio = 0.50 + 0.40 * confidence_score
            content_ratio = 1.0 - cf_ratio

            # 5. 构建详细信息（用于日志输出和论文分析）
            confidence_info = {
                'confidence_score': round(confidence_score, 4),
                'num_similar_users': num_similar_users,
                'avg_similarity': round(avg_similarity, 4),
                'user_rating_count': user_rating_count,
                'user_quantity_score': round(user_quantity_score, 4),
                'strategy': 'dynamic_confidence_based'
            }

            logger.info(
                f"动态比例计算: "
                f"相似用户={num_similar_users}个, "
                f"平均相似度={avg_similarity:.3f}, "
                f"置信度={confidence_score:.3f}, "
                f"→ 协同过滤={cf_ratio:.1%}, 内容特征={content_ratio:.1%}"
            )

            return cf_ratio, content_ratio, confidence_info

        except Exception as e:
            logger.error(f"动态比例计算失败，回退到固定7:3比例: {e}")
            # 出错时回退到原始的固定比例
            return 0.70, 0.30, {
                'confidence_score': None,
                'error': str(e),
                'strategy': 'fallback_fixed_ratio'
            }

    def _get_fallback_recommendations(self, top_n):
        """统一的降级推荐：前10本评分最高且人数最多的图书"""
        logger.info("使用统一降级策略：返回评分最高且评价人数最多的优质图书")
        return self.content_cf._get_top_quality_books(top_n)

    def _calculate_dynamic_item_ratio(self, target_book_id, cf_similar_books, content_similar_books):
        """
        基于目标图书的数据质量动态计算混合比例（图书详情页专用）

        核心思想：
        - 评分数量越多 → 协同过滤越可靠 → CF权重提升
        - 相似图书质量越高 → CF效果越好 → CF权重提升
        - 冷门图书数据稀疏 → 内容特征更安全 → Content权重提升

        公式：
            quantity_score = min(rating_count / 500, 1.0)
            cf_quality_score = min(cf_count / 20, 1.0) × cf_avg_similarity
            confidence = quantity_score × cf_quality_score
            cf_ratio = 0.40 + 0.45 × confidence  # 范围 [0.40, 0.85]

        参数:
            target_book_id: 目标图书ID
            cf_similar_books: 物品协同过滤找到的相似图书列表
            content_similar_books: 内容特征找到的相似图书列表

        返回:
            tuple: (cf_ratio, content_ratio, confidence_info)
                - cf_ratio: 协同过滤占比 [0.40, 0.85]
                - content_ratio: 内容特征占比 [0.15, 0.60]
                - confidence_info: 置信度详细信息
        """
        try:
            # 1. 获取目标图书的基本信息
            target_book_info = self.content_cf.books_df[
                self.content_cf.books_df['book_id'] == target_book_id
            ]

            if target_book_info.empty:
                logger.warning(f"图书 {target_book_id} 不存在于数据库中，使用默认比例 50:50")
                return 0.50, 0.50, {
                    'strategy': 'book_not_found',
                    'reason': '目标图书不存在'
                }

            # 2. 提取图书数据质量指标
            target_book_data = target_book_info.iloc[0]
            rating_count = int(target_book_data['rating_count'])
            avg_rating = float(target_book_data['avg_rating'])

            # 3. 评分数量归一化得分 [0, 1]
            # 设定500个评分为满分（基于Book-Crossing数据集的中位数分析）
            # 超过500个评分的图书，协同过滤已经非常可靠
            quantity_score = min(rating_count / 100.0, 1.0)

            # 4. 协同过滤结果质量评估
            if cf_similar_books and len(cf_similar_books) > 0:
                # 4.1 相似图书数量得分 [0, 1]
                # 20本相似书为满分（一般找到20本以上说明数据很充足）
                cf_count = len(cf_similar_books)
                cf_count_score = min(cf_count / 20.0, 1.0)

                # 4.2 计算平均相似度 [0, 1]
                cf_similarities = [book.get('similarity', 0) for book in cf_similar_books]
                cf_avg_similarity = np.mean(cf_similarities) if cf_similarities else 0.0

                # 4.3 协同过滤质量得分 = 数量得分 × 相似度质量
                # 这个公式体现了"数量"和"质量"的双重考量
                cf_quality_score = cf_count_score * cf_avg_similarity
            else:
                # 没有协同过滤结果，质量得分为0
                cf_count = 0
                cf_avg_similarity = 0.0
                cf_quality_score = 0.0

            # 5. 综合置信度分数 = 图书数据质量 × CF算法质量
            # 只有当图书本身评分多 AND 找到了高质量相似图书时，置信度才会高
            confidence_score = quantity_score * cf_quality_score

            # 6. 映射到协同过滤比例
            # 基准线：40% (极冷门书，内容特征占主导 60%)
            # 最大值：85% (超热门书，协同过滤高度可靠)
            # 设计理念：即使是冷门书，也给协同过滤保留40%的机会
            #          即使是热门书，也给内容特征保留15%的多样性
            MIN_CF_RATIO = 0.40
            MAX_CF_RATIO = 0.85
            cf_ratio = MIN_CF_RATIO + (MAX_CF_RATIO - MIN_CF_RATIO) * confidence_score
            content_ratio = 1.0 - cf_ratio

            # 7. 构建详细置信度信息（用于日志输出和调试分析）
            confidence_info = {
                'rating_count': rating_count,
                'avg_rating': round(avg_rating, 2),
                'quantity_score': round(quantity_score, 4),
                'cf_similar_count': cf_count,
                'cf_avg_similarity': round(cf_avg_similarity, 4),
                'cf_count_score': round(cf_count_score, 4) if cf_count > 0 else 0.0,
                'cf_quality_score': round(cf_quality_score, 4),
                'confidence_score': round(confidence_score, 4),
                'strategy': 'item_quality_adaptive',
                'formula': f'cf_ratio = {MIN_CF_RATIO} + {MAX_CF_RATIO - MIN_CF_RATIO} × confidence'
            }

            # 8. 输出详细日志
            logger.info(
                f"[图书详情动态比例] 图书ID={target_book_id}: "
                f"评分数={rating_count}, "
                f"数量得分={quantity_score:.2f}, "
                f"CF相似书={cf_count}本, "
                f"CF平均相似度={cf_avg_similarity:.2f}, "
                f"CF质量得分={cf_quality_score:.2f}, "
                f"综合置信度={confidence_score:.3f} → "
                f"协同过滤={cf_ratio:.1%}, 内容特征={content_ratio:.1%}"
            )

            return cf_ratio, content_ratio, confidence_info

        except Exception as e:
            logger.error(f"动态比例计算失败，回退到默认比例 70:30: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0.70, 0.30, {
                'strategy': 'fallback_fixed_ratio',
                'error': str(e),
                'reason': '计算异常，使用固定比例'
            }

    def get_hybrid_similar_books(self, target_book_id, top_k=6):
        """
        动态混合相似图书推荐（图书详情页专用）

        策略：根据目标图书的数据质量动态调整协同过滤和内容特征的混合比例
        - 热门书（评分多、相似书多）：协同过滤权重高 (70%-85%)
        - 冷门书（评分少、相似书少）：内容特征权重高 (55%-60%)

        参数:
            target_book_id: 目标图书ID
            top_k: 返回推荐数量（默认6本）

        返回:
            list: 推荐图书列表，每个推荐包含动态比例元数据
        """
        logger.info(f"为图书 {target_book_id} 生成动态混合相似推荐...")

        try:
            # 1. 获取物品协同过滤推荐
            cf_similar = self.item_cf.get_similar_books_for_item(target_book_id, top_k * 2)
            logger.info(f"物品协同过滤找到 {len(cf_similar) if cf_similar else 0} 本相似图书")

            # 2. 获取内容特征推荐
            content_similar = self.content_cf.get_similar_books_by_content(target_book_id, top_k * 2)
            logger.info(f"内容特征找到 {len(content_similar) if content_similar else 0} 本相似图书")

            # 3. 根据结果选择推荐策略
            if cf_similar and content_similar:
                # 【情况1】两种算法都有结果 → 动态混合推荐（核心改进）
                logger.info("[情况1] 物品协同 + 内容特征都有结果，使用动态混合策略")

                # 3.1 动态计算混合比例
                dynamic_cf_ratio, dynamic_content_ratio, confidence_info = \
                    self._calculate_dynamic_item_ratio(target_book_id, cf_similar, content_similar)

                # 3.2 按动态比例混合推荐
                mixed_similar = self._mix_recommendations(
                    cf_similar, content_similar, dynamic_cf_ratio, top_k
                )

                # 3.3 为每个推荐添加元数据
                for rec in mixed_similar:
                    rec['mixing_strategy'] = 'dynamic_item_cf_content'
                    rec['cf_ratio'] = round(dynamic_cf_ratio, 2)
                    rec['content_ratio'] = round(dynamic_content_ratio, 2)
                    rec['confidence_info'] = confidence_info
                    rec['algorithm'] = 'item_quality_adaptive'

                logger.info(
                    f"动态混合推荐完成: CF {dynamic_cf_ratio:.1%} + Content {dynamic_content_ratio:.1%}, "
                    f"返回 {len(mixed_similar)} 个推荐"
                )
                return mixed_similar

            elif cf_similar:
                # 【情况2】仅物品协同有结果 → 纯协同过滤
                logger.info("[情况2] 仅物品协同过滤有结果，使用纯协同过滤推荐")
                result = cf_similar[:top_k]

                # 添加元数据
                for rec in result:
                    rec['mixing_strategy'] = 'item_cf_only'
                    rec['cf_ratio'] = 1.0
                    rec['content_ratio'] = 0.0
                    rec['algorithm'] = 'item_based_cf_only'
                    rec['reason'] = '基于评分模式的协同过滤推荐'

                logger.info(f"纯协同过滤推荐完成，返回 {len(result)} 个推荐")
                return result

            elif content_similar:
                # 【情况3】仅内容特征有结果 → 纯内容推荐
                logger.info("[情况3] 仅内容特征有结果，使用纯内容特征推荐")
                result = content_similar[:top_k]

                # 添加元数据
                for rec in result:
                    rec['mixing_strategy'] = 'content_only'
                    rec['cf_ratio'] = 0.0
                    rec['content_ratio'] = 1.0
                    rec['algorithm'] = 'content_based_only'
                    rec['reason'] = '基于标题作者出版社的内容特征推荐'

                logger.info(f"纯内容特征推荐完成，返回 {len(result)} 个推荐")
                return result

            else:
                # 【情况4】两种算法都无结果 → 降级到同作者推荐
                logger.warning("[情况4] 物品协同和内容特征都无结果，降级到同作者图书推荐")
                result = self._get_same_author_books(target_book_id, top_k)

                # 添加元数据
                for rec in result:
                    rec['mixing_strategy'] = 'same_author_fallback'
                    rec['cf_ratio'] = 0.0
                    rec['content_ratio'] = 0.0
                    # algorithm 已在 _get_same_author_books 中设置

                logger.info(f"同作者推荐完成，返回 {len(result)} 个推荐")
                return result

        except Exception as e:
            logger.error(f"图书详情页推荐失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
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