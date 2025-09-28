<template>
  <div class="my-ratings">
    <div class="header-section">
      <h1>我的评分</h1>
      <p>查看您评分过的所有图书</p>
    </div>
    
    <div class="ratings-content" v-loading="loading">
      <div v-if="userRatings.length > 0" class="ratings-grid">
        <div 
          v-for="rating in userRatings" 
          :key="rating.ratingId"
          class="rating-card"
          @click="$router.push(`/books/${rating.bookId}`)"
        >
          <div class="book-cover">
            <img 
              :src="rating.imageUrlM || '/default-book.jpg'" 
              :alt="rating.title"
              @error="handleImageError"
            />
          </div>
          <div class="book-info">
            <h4 class="book-title">{{ rating.title }}</h4>
            <p class="book-author">{{ rating.author || '未知作者' }}</p>
            <div class="rating-info">
              <el-rate :model-value="parseFloat(rating.rating)" disabled />
              <span class="my-rating">{{ rating.rating }}分</span>
            </div>
            <div class="book-meta">
              <span class="book-year">{{ rating.year || '未知年份' }}</span>
              <span class="rating-date">{{ formatDate(rating.ratingDate) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <el-empty v-else description="您还没有评分过任何图书" :image-size="120">
        <el-button type="primary" @click="$router.push('/books')">去评分图书</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const loading = ref(false)
const userRatings = ref([])

const loadUserRatings = async () => {
  if (!userStore.user) {
    ElMessage.error('请先登录')
    return
  }
  
  loading.value = true
  try {
    const response = await userApi.getUserRatings(userStore.user.userId)
    userRatings.value = response.data || []
  } catch (error) {
    ElMessage.error('加载评分历史失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleImageError = (event) => {
  event.target.src = '/default-book.jpg'
}

onMounted(() => {
  loadUserRatings()
})
</script>

<style scoped>
.my-ratings {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.header-section h1 {
  color: #333;
  margin-bottom: 10px;
}

.header-section p {
  color: #666;
  font-size: 16px;
}

.ratings-content {
  min-height: 400px;
}

.ratings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.rating-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.rating-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007aff;
}

.book-cover {
  text-align: center;
  margin-bottom: 15px;
}

.book-cover img {
  width: 100px;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
}

.book-title {
  font-size: 16px;
  font-weight: bold;
  margin: 10px 0 5px 0;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 44px;
}

.book-author {
  font-size: 14px;
  color: #666;
  margin: 5px 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rating-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
}

.my-rating {
  font-size: 16px;
  font-weight: bold;
  color: #007aff;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

.book-year {
  font-weight: 500;
}

.rating-date {
  font-style: italic;
}
</style>