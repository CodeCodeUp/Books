import request from '../utils/request'

export const recommendApi = {
  // 基于用户的协同过滤推荐
  getUserBasedRecommendations(userId, topN = 10, minRating = 3.0) {
    return request.post('/recommendations/user-based', null, {
      params: { userId, topN, minRating }
    })
  },
  
  // 获取相似用户
  getSimilarUsers(userId, topK = 10) {
    return request.post('/recommendations/similar-users', null, {
      params: { userId, topK }
    })
  },
  
  // 获取算法信息
  getAlgorithmInfo() {
    return request.get('/recommendations/algorithm/info')
  },
  
  // 检查推荐服务健康状态
  checkHealth() {
    return request.get('/recommendations/health')
  }
}