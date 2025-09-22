import json
import os
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class RecommendationCache:
    """推荐结果缓存管理器"""
    
    def __init__(self, cache_dir='models/cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_file(self, user_id: int) -> str:
        """获取用户缓存文件路径"""
        return os.path.join(self.cache_dir, f"user_{user_id}_recommendations.json")
    
    def save_recommendations(self, user_id: int, recommendations: List[Dict], algorithm: str):
        """保存推荐结果到缓存"""
        try:
            cache_data = {
                'user_id': user_id,
                'algorithm': algorithm,
                'recommendations': recommendations,
                'timestamp': time.time(),
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            cache_file = self._get_cache_file(user_id)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"用户 {user_id} 的推荐结果已缓存")
            
        except Exception as e:
            logger.error(f"保存推荐缓存失败: {e}")
    
    def load_recommendations(self, user_id: int, max_age: int = 3600) -> Optional[List[Dict]]:
        """从缓存加载推荐结果"""
        try:
            cache_file = self._get_cache_file(user_id)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            cache_age = time.time() - cache_data['timestamp']
            if cache_age > max_age:
                logger.info(f"用户 {user_id} 的缓存已过期（{cache_age:.0f}秒）")
                return None
            
            logger.info(f"从缓存加载用户 {user_id} 的推荐结果")
            return cache_data['recommendations']
            
        except Exception as e:
            logger.error(f"加载推荐缓存失败: {e}")
            return None
    
    def invalidate_user_cache(self, user_id: int):
        """清除用户缓存（用户评分后调用）"""
        try:
            cache_file = self._get_cache_file(user_id)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logger.info(f"用户 {user_id} 的缓存已清除")
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
    
    def is_cache_valid(self, user_id: int, max_age: int = 3600) -> bool:
        """检查缓存是否有效"""
        try:
            cache_file = self._get_cache_file(user_id)
            
            if not os.path.exists(cache_file):
                return False
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cache_age = time.time() - cache_data['timestamp']
            return cache_age <= max_age
            
        except Exception as e:
            return False