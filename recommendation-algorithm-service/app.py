from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback
from algorithms.collaborative_filtering import UserBasedCollaborativeFiltering
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

# 初始化推荐算法
user_cf = UserBasedCollaborativeFiltering()

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
    """基于用户的协同过滤推荐"""
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
        
        logger.info(f"收到推荐请求: user_id={user_id}, top_n={top_n}, min_rating={min_rating}")
        
        # 生成推荐
        recommendations = user_cf.get_recommendations(
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
                'algorithm_info': user_cf.get_algorithm_info()
            },
            'message': f'成功生成{len(recommendations)}个推荐'
        })
        
    except Exception as e:
        logger.error(f"推荐生成失败: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'推荐生成失败: {str(e)}'
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
                logger.info(f"开始为用户 {user_id} 预计算推荐...")
                recommendations = user_cf.get_recommendations(user_id)
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
                    user_cf.get_algorithm_info()
                ],
                'service_info': {
                    'name': 'recommendation-algorithm-service',
                    'version': '1.0.0',
                    'description': '图书推荐算法服务'
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
        user_cf.load_data()  # 启动时全量加载数据
        logger.info("数据初始化成功")
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        logger.error("请检查数据库连接后重试")
        exit(1)
    
    logger.info(f"服务地址: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info("API文档:")
    logger.info("  POST /api/recommend/user-based  - 用户协同过滤推荐")
    logger.info("  POST /api/recommend/similar-users - 获取相似用户")
    logger.info("  POST /api/cache/clear - 清除用户缓存")
    logger.info("  POST /api/cache/precompute - 预计算推荐")
    logger.info("  GET  /api/algorithm/info - 获取算法信息")
    logger.info("  GET  /health - 健康检查")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )