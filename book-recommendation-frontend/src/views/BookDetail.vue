<template>
  <div class="book-detail" v-loading="loading">
    <el-card v-if="book">
      <div class="book-content">
        <div class="book-image">
          <img 
            :src="book.imageUrlL || '/default-book.jpg'" 
            :alt="book.title"
            @error="handleImageError"
          />
        </div>
        
        <div class="book-info">
          <h1>{{ book.title }}</h1>
          <p class="author">作者：{{ book.author || '未知' }}</p>
          <p class="publisher">出版社：{{ book.publisher || '未知' }}</p>
          <p class="year">出版年份：{{ book.year || '未知' }}</p>
          
          <div class="rating-section">
            <div class="rating-display">
              <el-rate 
                v-model="displayRating" 
                disabled 
                show-score 
                :score-template="`${book.avgRating || 0}`"
              />
              <span class="rating-text">
                {{ book.avgRating || 0 }}分 ({{ book.ratingCount || 0 }}人评价)
              </span>
            </div>
            
            <!-- 用户评分功能 -->
            <div class="user-rating" v-if="userStore.isLoggedIn">
              <span>我的评分：</span>
              <el-rate 
                v-model="userRating" 
                @change="handleRating"
                :allow-half="true"
                :max="5"
                show-score
              />
              <span class="rating-tip">支持0.5分间隔评分</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
    
    <el-empty v-else-if="!loading" description="图书不存在" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { bookApi } from '../api/book'
import { ratingApi } from '../api/rating'
import { ElMessage } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()

const book = ref(null)
const loading = ref(false)
const userRating = ref(0)

const displayRating = computed(() => {
  return book.value?.avgRating || 0
})

const loadBookDetail = async () => {
  loading.value = true
  try {
    const response = await bookApi.getBookDetail(route.params.bookId)
    book.value = response.data
    
    // 加载用户对该图书的评分
    if (userStore.isLoggedIn) {
      loadUserRating()
    }
  } catch (error) {
    ElMessage.error('加载图书详情失败')
  } finally {
    loading.value = false
  }
}

const loadUserRating = async () => {
  if (!userStore.user) return
  
  try {
    const response = await ratingApi.getUserBookRating(userStore.user.userId, route.params.bookId)
    if (response.data) {
      userRating.value = parseFloat(response.data.rating)
    }
  } catch (error) {
    // 用户未评分，忽略错误
    userRating.value = 0
  }
}

const handleRating = async (value) => {
  if (!userStore.user) {
    ElMessage.error('请先登录')
    return
  }
  
  try {
    await ratingApi.rateBook(userStore.user.userId, route.params.bookId, value)
    ElMessage.success(`评分成功：${value}分`)
    
    // 重新加载图书信息以更新平均评分
    setTimeout(() => {
      loadBookDetail()
    }, 500)
  } catch (error) {
    ElMessage.error('评分失败')
    loadUserRating() // 恢复原评分
  }
}

const handleImageError = (event) => {
  event.target.src = '/default-book.jpg'
}

onMounted(() => {
  loadBookDetail()
})
</script>

<style scoped>
.book-detail {
  max-width: 800px;
  margin: 0 auto;
}

.book-content {
  display: flex;
  gap: 30px;
}

.book-image {
  flex-shrink: 0;
}

.book-image img {
  width: 200px;
  height: 280px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.book-info {
  flex: 1;
}

.book-info h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 15px;
}

.book-info p {
  font-size: 16px;
  color: #666;
  margin: 8px 0;
}

.rating-section {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.rating-display {
  margin-bottom: 15px;
}

.rating-text {
  margin-left: 10px;
  color: #666;
}

.user-rating {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rating-tip {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}
</style>