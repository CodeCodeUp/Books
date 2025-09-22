import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    DB_CONFIG = {
        'host': '116.205.244.106',
        'port': 3306,
        'user': 'root',
        'password': '202358hjq',
        'database': 'book_recommendation',
        'charset': 'utf8mb4'
    }
    
    # Flask配置
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
    FLASK_DEBUG = False  # 关闭debug模式，避免重复初始化
    
    # 推荐算法参数
    DEFAULT_TOP_N = 10
    MIN_COMMON_RATINGS = 5  # 计算用户相似度的最少共同评分数
    MIN_SIMILARITY = 0.1    # 最小相似度阈值
    MAX_NEIGHBORS = 50      # 最大邻居用户数
    
    # 缓存配置
    CACHE_DURATION = 3600   # 推荐结果缓存1小时