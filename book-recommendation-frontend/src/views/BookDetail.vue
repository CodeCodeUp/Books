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
              <el-rate v-model="userRating" @change="handleRating" />
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
  } catch (error) {
    ElMessage.error('加载图书详情失败')
  } finally {
    loading.value = false
  }
}

const handleRating = (value) => {
  // 这里可以调用评分API
  ElMessage.success(`您给这本书评了${value}分`)
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
</style>