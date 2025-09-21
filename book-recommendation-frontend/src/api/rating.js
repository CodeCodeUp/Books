import request from '../utils/request'

export const ratingApi = {
  // 用户评分
  rateBook(userId, bookId, rating) {
    return request.post('/ratings/rate', null, {
      params: { userId, bookId, rating }
    })
  },
  
  // 获取用户对图书的评分
  getUserBookRating(userId, bookId) {
    return request.get(`/ratings/user/${userId}/book/${bookId}`)
  },
  
  // 获取用户的所有评分
  getUserRatings(userId) {
    return request.get(`/ratings/user/${userId}`)
  },
  
  // 获取图书的所有评分
  getBookRatings(bookId) {
    return request.get(`/ratings/book/${bookId}`)
  }
}