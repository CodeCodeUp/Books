<template>
  <div class="home">
    <div class="hero-section">
      <h1>图书推荐系统</h1>
      <p>基于协同过滤与内容特征的智能推荐</p>
    </div>
    
    <div class="content-section">
      <!-- 热门图书 -->
      <div class="book-section">
        <h2>热门图书</h2>
        <div class="book-grid" v-loading="popularLoading">
          <BookCard 
            v-for="book in popularBooks" 
            :key="book.bookId" 
            :book="book" 
          />
        </div>
      </div>
      
      <!-- 最新图书 -->
      <div class="book-section">
        <h2>最新图书</h2>
        <div class="book-grid" v-loading="latestLoading">
          <BookCard 
            v-for="book in latestBooks" 
            :key="book.bookId" 
            :book="book" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bookApi } from '../api/book'
import BookCard from '../components/BookCard.vue'
import { ElMessage } from 'element-plus'

const popularBooks = ref([])
const latestBooks = ref([])
const popularLoading = ref(false)
const latestLoading = ref(false)

const loadPopularBooks = async () => {
  popularLoading.value = true
  try {
    const response = await bookApi.getPopularBooks(8)
    popularBooks.value = response.data || []
  } catch (error) {
    ElMessage.error('加载热门图书失败')
  } finally {
    popularLoading.value = false
  }
}

const loadLatestBooks = async () => {
  latestLoading.value = true
  try {
    const response = await bookApi.getLatestBooks(8)
    latestBooks.value = response.data || []
  } catch (error) {
    ElMessage.error('加载最新图书失败')
  } finally {
    latestLoading.value = false
  }
}

onMounted(() => {
  loadPopularBooks()
  loadLatestBooks()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.hero-section p {
  font-size: 1.2em;
  opacity: 0.9;
}

.content-section {
  padding: 0 20px;
}

.book-section {
  margin-bottom: 40px;
}

.book-section h2 {
  margin-bottom: 20px;
  color: #333;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
</style>