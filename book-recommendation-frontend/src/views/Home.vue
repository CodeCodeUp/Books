<template>
  <div class="home">
    <!-- 英雄区域 - 苹果风格 -->
    <div class="hero-section" data-aos="fade-up">
      <div class="hero-content">
        <h1 class="hero-title">
          智能图书推荐系统
        </h1>
        <p class="hero-subtitle">
          基于协同过滤与内容特征的个性化推荐
        </p>
        <div class="hero-buttons">
          <button 
            class="btn-primary"
            @click="$router.push('/books')"
          >
            <el-icon><Search /></el-icon>
            探索图书
          </button>
          <button 
            class="btn-secondary"
            @click="$router.push('/register')"
            v-if="!userStore.isLoggedIn"
          >
            开始使用
          </button>
        </div>
        <!-- 统计数据 - 苹果风格 -->
        <div class="stats-container">
          <div class="stat-card">
            <div class="stat-number" ref="bookCountRef">0</div>
            <div class="stat-label">图书收录</div>
          </div>
          <div class="stat-card">
            <div class="stat-number" ref="userCountRef">0</div>
            <div class="stat-label">活跃用户</div>
          </div>
          <div class="stat-card">
            <div class="stat-number" ref="ratingCountRef">0</div>
            <div class="stat-label">评分记录</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 内容区域 - 苹果风格布局 -->
    <div class="content-section">
      <!-- 热门图书区域 -->
      <div class="book-section" data-aos="fade-up">
        <div class="section-header">
          <h2 class="section-title">热门推荐</h2>
          <p class="section-subtitle">精选高评分图书为你推荐</p>
        </div>
        <div class="book-container">
          <Transition name="fade" mode="out-in">
            <div v-if="popularLoading" class="loading-container" key="loading">
              <HourglassLoader text="加载热门图书..." size="64px" />
            </div>
            <div v-else class="book-grid" key="content">
              <div
                v-for="(book, index) in popularBooks"
                :key="book.bookId"
                class="book-item"
                :data-aos="'fade-up'"
                :data-aos-delay="index * 100"
              >
                <BookCard :book="book" />
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <!-- 最新图书区域 -->
      <div class="book-section" data-aos="fade-up">
        <div class="section-header">
          <h2 class="section-title">最新上架</h2>
          <p class="section-subtitle">发现新鲜好书，拓展阅读视野</p>
        </div>
        <div class="book-container">
          <Transition name="fade" mode="out-in">
            <div v-if="latestLoading" class="loading-container" key="loading">
              <HourglassLoader text="加载最新图书..." size="64px" />
            </div>
            <div v-else class="book-grid" key="content">
              <div
                v-for="(book, index) in latestBooks"
                :key="book.bookId"
                class="book-item"
                :data-aos="'fade-up'"
                :data-aos-delay="index * 100"
              >
                <BookCard :book="book" />
              </div>
            </div>
          </Transition>
        </div>
      </div>
      
      <!-- 推荐算法展示 - 苹果风格 -->
      <div class="features-section" data-aos="fade-up">
        <div class="section-header">
          <h2 class="section-title">智能推荐技术</h2>
          <p class="section-subtitle">先进算法为你提供个性化阅读体验</p>
        </div>
        <div class="features-grid">
          <div class="feature-card" data-aos="fade-up" data-aos-delay="100">
            <div class="feature-icon">
              <div class="icon-bg collaborative"></div>
              🤝
            </div>
            <h3>协同过滤</h3>
            <p>基于用户行为和相似度分析，为您推荐志趣相投用户喜欢的优质图书</p>
          </div>
          <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
            <div class="feature-icon">
              <div class="icon-bg content"></div>
              🎯
            </div>
            <h3>内容特征</h3>
            <p>深度分析图书内容特征，智能匹配您的阅读偏好和兴趣方向</p>
          </div>
          <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <div class="feature-icon">
              <div class="icon-bg hybrid"></div>
              ⚡
            </div>
            <h3>混合推荐</h3>
            <p>融合多种算法优势，提供更加精准个性化的智能推荐结果</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useUserStore } from '../stores/user'
import { bookApi } from '../api/book'
import BookCard from '../components/BookCard.vue'
import HourglassLoader from '../components/HourglassLoader.vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const userStore = useUserStore()
const popularBooks = ref([])
const latestBooks = ref([])
const popularLoading = ref(false)
const latestLoading = ref(false)

// 数字动画引用
const bookCountRef = ref()
const userCountRef = ref()
const ratingCountRef = ref()

// 数字动画函数
const animateNumber = (element, target, duration = 2000) => {
  let start = 0
  const increment = target / (duration / 16)
  
  const animate = () => {
    start += increment
    if (start < target) {
      element.textContent = Math.floor(start).toLocaleString()
      requestAnimationFrame(animate)
    } else {
      element.textContent = target.toLocaleString()
    }
  }
  animate()
}

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

onMounted(async () => {
  await loadPopularBooks()
  await loadLatestBooks()
  
  // 延迟初始化确保DOM已渲染
  await nextTick()
  
  // 启动数字动画
  setTimeout(() => {
    if (bookCountRef.value) animateNumber(bookCountRef.value, 271360)
    if (userCountRef.value) animateNumber(userCountRef.value, 77805, 2500)
    if (ratingCountRef.value) animateNumber(ratingCountRef.value, 433671, 3000)
  }, 1000)
})
</script>

<style scoped>
/* 苹果风格全局样式 */
.home {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 英雄区域 - 苹果风格 */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  padding: 120px 20px 80px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  z-index: 2;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 24px;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 1.375rem;
  color: #86868b;
  margin-bottom: 48px;
  font-weight: 400;
  line-height: 1.4;
}

.hero-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 80px;
  flex-wrap: wrap;
}

/* 苹果风格按钮 */
.btn-primary {
  background: #007aff;
  color: white;
  border: none;
  border-radius: 22px;
  padding: 12px 24px;
  font-size: 17px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.3);
}

.btn-primary:hover {
  background: #0056cc;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
  border: none;
  border-radius: 22px;
  padding: 12px 24px;
  font-size: 17px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

/* 统计数据 - 苹果风格卡片 */
.stats-container {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.stat-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  min-width: 140px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #007aff;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #86868b;
  font-weight: 500;
}

/* 内容区域 - 苹果风格 */
.content-section {
  position: relative;
  background: #fafafa;
  padding: 80px 20px;
}

.book-section {
  max-width: 1200px;
  margin: 0 auto 100px auto;
}

.features-section {
  max-width: 1200px;
  margin: 0 auto;
}

/* 区域标题 - 苹果风格 */
.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 1.1rem;
  color: #86868b;
  font-weight: 400;
  line-height: 1.4;
}

/* 图书容器 */
.book-container {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

/* 加载容器 */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

/* 淡入淡出过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.book-item {
  transition: all 0.3s ease;
}

.book-item:hover {
  transform: translateY(-4px);
}

/* 特性卡片 - 苹果风格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 32px;
  margin-top: 60px;
}

.feature-card {
  background: white;
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  border: 1px solid rgba(0, 0, 0, 0.04);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  position: relative;
  font-size: 3rem;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-bg {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  z-index: -1;
  opacity: 0.1;
}

.icon-bg.collaborative {
  background: #007aff;
}

.icon-bg.content {
  background: #ff9500;
}

.icon-bg.hybrid {
  background: #34c759;
}

.feature-card h3 {
  font-size: 1.375rem;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}

.feature-card p {
  font-size: 1rem;
  line-height: 1.5;
  color: #86868b;
  font-weight: 400;
}

/* 响应式设计 - 苹果风格 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
  
  .stats-container {
    gap: 20px;
  }
  
  .stat-card {
    min-width: 120px;
    padding: 20px;
  }
  
  .stat-number {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .book-container {
    padding: 24px;
  }
  
  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .feature-card {
    padding: 32px 24px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-section {
    padding: 100px 16px 60px;
  }
  
  .content-section {
    padding: 60px 16px;
  }
  
  .book-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-container {
    gap: 16px;
  }
  
  .stat-card {
    min-width: 100px;
    padding: 16px;
  }
}
</style>