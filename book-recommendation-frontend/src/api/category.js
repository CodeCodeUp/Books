import request from '../utils/request'

export const categoryApi = {
  // 获取所有主题
  getAllCategories() {
    return request.get('/themes')
  },

  // 根据ID获取主题信息
  getCategoryById(categoryId) {
    return request.get(`/themes/${categoryId}`)
  }
}
