import request from '../utils/request'

export const bookApi = {
  // 分页查询图书
  getBooks(page = 1, size = 20, keyword = '') {
    return request.get('/books', {
      params: { page, size, keyword }
    })
  },
  
  // 获取图书详情
  getBookDetail(bookId) {
    return request.get(`/books/${bookId}`)
  },
  
  // 获取热门图书
  getPopularBooks(limit = 10) {
    return request.get('/books/popular', {
      params: { limit }
    })
  },
  
  // 获取最新图书
  getLatestBooks(limit = 10) {
    return request.get('/books/latest', {
      params: { limit }
    })
  },
  
  // 获取相似图书
  getSimilarBooks(bookId, userId = null, limit = 6) {
    return request.get(`/books/${bookId}/similar`, {
      params: { userId, limit }
    })
  },
  
  // 获取图书的所有评分
  getBookRatings(bookId) {
    return request.get(`/books/${bookId}/ratings`)
  }
}