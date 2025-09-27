from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback
from algorithms.collaborative_filtering import UserBasedCollaborativeFiltering
from algorithms.item_based_cf import ItemBasedCollaborativeFiltering
from algorithms.hybrid import HybridRecommendation
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化推荐算法（共享数据加载器）
user_cf = UserBasedCollaborativeFiltering()
item_cf = ItemBasedCollaborativeFiltering(shared_data_loader=user_cf.data_loader)
hybrid = HybridRecommendation(shared_data_loader=user_cf.data_loader)

# 设置混合推荐的算法实例引用
hybrid.user_cf = user_cf
hybrid.item_cf = item_cf

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'recommendation-algorithm-service',
        'version': '1.0.0'
    })

@app.route('/api/recommend/user-based', methods=['POST'])
def recommend_user_based():
    """混合推荐：用户协同过滤 + 内容特征"""
    try:
        # 获取请求参数
        data = request.get_json()
        user_id = data.get('user_id')
        top_n = data.get('top_n', Config.DEFAULT_TOP_N)
        min_rating = data.get('min_rating', 3.0)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id参数必须提供'
            }), 400
        
        logger.info(f"收到混合推荐请求: user_id={user_id}, top_n={top_n}, min_rating={min_rating}")
        
        # 使用混合推荐策略
        recommendations = hybrid.get_hybrid_user_recommendations(
            user_id=user_id,
            top_n=top_n
        )
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'recommendations': recommendations,
                'total': len(recommendations),
                'algorithm_info': {
                    'name': '混合推荐算法',
                    'type': 'hybrid_recommendation',
                    'description': '用户协同过滤70% + 内容特征30%'
                }
            },
            'message': f'成功生成{len(recommendations)}个混合推荐'
        })
        
    except Exception as e:
        logger.error(f"混合推荐失败: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'推荐生成失败: {str(e)}'
        }), 500

@app.route('/api/recommend/item-based', methods=['POST'])
def recommend_item_based():
    """基于物品的协同过滤推荐"""
    try:
        # 获取请求参数
        data = request.get_json()
        user_id = data.get('user_id')
        top_n = data.get('top_n', Config.DEFAULT_TOP_N)
        min_rating = data.get('min_rating', 3.0)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id参数必须提供'
            }), 400
        
        logger.info(f"收到物品协同过滤推荐请求: user_id={user_id}, top_n={top_n}, min_rating={min_rating}")
        
        # 生成推荐
        recommendations = item_cf.get_recommendations(
            user_id=user_id,
            top_n=top_n,
            min_rating=min_rating
        )
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'recommendations': recommendations,
                'total': len(recommendations),
                'algorithm_info': item_cf.get_algorithm_info()
            },
            'message': f'成功生成{len(recommendations)}个推荐'
        })
        
    except Exception as e:
        logger.error(f"物品协同过滤推荐失败: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'推荐生成失败: {str(e)}'
        }), 500

@app.route('/api/recommend/similar-items', methods=['POST'])
def get_similar_items():
    """混合相似图书：物品协同过滤 + 内容特征"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        top_k = data.get('top_k', 6)
        
        if not item_id:
            return jsonify({
                'success': False,
                'message': 'item_id参数必须提供'
            }), 400
        
        # 使用混合相似图书推荐
        similar_books = hybrid.get_hybrid_similar_books(item_id, top_k)
        
        return jsonify({
            'success': True,
            'data': {
                'item_id': item_id,
                'similar_books': similar_books,
                'total': len(similar_books)
            }
        })
        
    except Exception as e:
        logger.error(f"获取混合相似图书失败: {e}")
        
        return jsonify({
            'success': False,
            'message': f'获取相似图书失败: {str(e)}'
        }), 500

@app.route('/api/recommend/similar-users', methods=['POST'])
def get_similar_users():
    """获取相似用户"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        top_k = data.get('top_k', 10)
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id参数必须提供'
            }), 400
        
        # 找到相似用户
        similar_users = user_cf.find_similar_users(user_id, top_k)
        
        # 转换为列表格式
        similar_users_list = [
            {
                'user_id': int(uid),
                'similarity': float(sim)
            }
            for uid, sim in similar_users.items()
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'similar_users': similar_users_list,
                'total': len(similar_users_list)
            }
        })
        
    except Exception as e:
        logger.error(f"获取相似用户失败: {e}")
        
        return jsonify({
            'success': False,
            'message': f'获取相似用户失败: {str(e)}'
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_user_cache():
    """清除用户推荐缓存（用户评分后调用）"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id参数必须提供'
            }), 400
        
        # 清除缓存
        user_cf.cache.invalidate_user_cache(user_id)
        
        logger.info(f"已清除用户 {user_id} 的推荐缓存")
        
        return jsonify({
            'success': True,
            'message': f'用户 {user_id} 的缓存已清除'
        })
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        
        return jsonify({
            'success': False,
            'message': f'清除缓存失败: {str(e)}'
        }), 500

@app.route('/api/cache/precompute', methods=['POST'])
def precompute_recommendations():
    """预计算用户推荐（异步后台任务）"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'user_id参数必须提供'
            }), 400
        
        # 异步预计算推荐
        import threading
        
        def compute_in_background():
            try:
                logger.info(f"开始为用户 {user_id} 预计算混合推荐...")
                
                # 强制刷新数据，确保获取最新评分
                logger.info("强制刷新数据以获取最新评分...")
                user_cf.ratings_df = user_cf.data_loader.get_ratings_data(force_refresh=True)
                user_cf.books_df = user_cf.data_loader.get_books_data(force_refresh=True)
                
                # 同步更新混合推荐的数据
                hybrid.content_cf.ratings_df = user_cf.ratings_df
                hybrid.content_cf.books_df = user_cf.books_df
                
                recommendations = hybrid.get_hybrid_user_recommendations(user_id)
                logger.info(f"用户 {user_id} 预计算完成，生成{len(recommendations)}个推荐")
            except Exception as e:
                logger.error(f"预计算失败: {e}")
        
        thread = threading.Thread(target=compute_in_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'用户 {user_id} 的推荐预计算已启动'
        })
        
    except Exception as e:
        logger.error(f"启动预计算失败: {e}")
        
        return jsonify({
            'success': False,
            'message': f'启动预计算失败: {str(e)}'
        }), 500

@app.route('/api/algorithm/info', methods=['GET'])
def get_algorithm_info():
    """获取算法信息"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'available_algorithms': [
                    user_cf.get_algorithm_info(),
                    item_cf.get_algorithm_info(),
                    hybrid.content_cf.get_algorithm_info(),
                    {
                        'name': '混合推荐算法',
                        'type': 'hybrid_recommendation',
                        'description': '协同过滤与内容特征的智能混合',
                        'strategy': '协同过滤70% + 内容特征30%',
                        'fallback': '自动降级处理冷启动问题'
                    }
                ],
                'service_info': {
                    'name': 'recommendation-algorithm-service',
                    'version': '2.0.0',
                    'description': '图书推荐算法服务 - 支持混合推荐策略'
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取算法信息失败: {e}")
        
        return jsonify({
            'success': False,
            'message': f'获取算法信息失败: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'API接口不存在'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    logger.info("=== 启动图书推荐算法服务 ===")
    
    # 启动时初始化数据
    logger.info("正在初始化数据...")
    try:
        user_cf.load_data()  # 只初始化一次数据
        item_cf.load_data()  # 使用共享数据
        hybrid.load_data()   # 混合推荐算法初始化
        logger.info("混合推荐算法数据初始化成功")
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        logger.error("请检查数据库连接后重试")
        exit(1)
    
    logger.info(f"服务地址: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info("API文档:")
    logger.info("  POST /api/recommend/user-based   - 混合推荐(用户协同70%+内容30%)")
    logger.info("  POST /api/recommend/item-based   - 物品协同过滤推荐")
    logger.info("  POST /api/recommend/similar-users - 获取相似用户")
    logger.info("  POST /api/recommend/similar-items - 混合相似图书(物品协同70%+内容30%)")
    logger.info("  POST /api/cache/clear - 清除用户缓存")
    logger.info("  POST /api/cache/precompute - 预计算推荐")
    logger.info("  GET  /api/algorithm/info - 获取算法信息")
    logger.info("  GET  /health - 健康检查")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )