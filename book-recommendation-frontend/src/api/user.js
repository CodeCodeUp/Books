import request from '../utils/request'

export const userApi = {
  // 用户注册
  register(username, password, email) {
    return request.post('/users/register', null, {
      params: { username, password, email }
    })
  },
  
  // 用户登录
  login(username, password) {
    return request.post('/users/login', null, {
      params: { username, password }
    })
  },
  
  // 获取用户信息
  getUserInfo(userId) {
    return request.get(`/users/${userId}`)
  },
  
  // 更新用户信息
  updateUserInfo(userId, userInfo) {
    const { nickname, email, location, age, country } = userInfo
    return request.put(`/users/${userId}`, null, {
      params: { nickname, email, location, age, country }
    })
  },
  
  // 获取用户评分历史
  getUserRatings(userId) {
    return request.get(`/users/${userId}/ratings`)
  }
}