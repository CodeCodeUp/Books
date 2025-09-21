<template>
  <div class="book-card-wrapper">
    <el-card 
      :class="['book-card', { 'enhanced': enhanced }]" 
      @click="goToDetail" 
      shadow="hover"
    >
      <div class="book-image-container">
        <div class="book-image">
          <img 
            :src="book.imageUrlM || '/default-book.jpg'" 
            :alt="book.title"
            @error="handleImageError"
            class="book-cover"
          />
          <div class="image-overlay">
            <el-icon class="view-icon"><View /></el-icon>
          </div>
        </div>
        <!-- 热门标签 -->
        <div v-if="isPopular" class="popular-badge">
          <el-icon><Star /></el-icon>
          热门
        </div>
        <!-- 新书标签 -->
        <div v-if="isNew" class="new-badge">
          NEW
        </div>
      </div>
      
      <div class="book-info">
        <h3 class="book-title" :title="book.title">{{ book.title }}</h3>
        <p class="book-author" :title="book.author">{{ book.author || '未知作者' }}</p>
        
        <div class="book-meta">
          <div class="book-year" v-if="book.year">
            <el-icon><Calendar /></el-icon>
            {{ book.year }}
          </div>
          <div class="book-publisher" v-if="book.publisher" :title="book.publisher">
            <el-icon><House /></el-icon>
            {{ truncateText(book.publisher, 10) }}
          </div>
        </div>
        
        <div class="book-stats">
          <div class="rating-section">
            <el-rate 
              v-model="displayRating" 
              disabled 
              size="small"
              :colors="ratingColors"
            />
            <span class="rating-score">{{ formatRating(book.avgRating) }}</span>
          </div>
          <div class="rating-count">({{ book.ratingCount || 0 }}人评价)</div>
        </div>
        
        <!-- 增强模式下的额外信息 -->
        <div v-if="enhanced" class="enhanced-info">
          <div class="action-buttons">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="handleQuickAction('favorite')"
              :icon="StarFilled"
            >
              收藏
            </el-button>
            <el-button 
              size="small" 
              @click.stop="handleQuickAction('rate')"
              :icon="Star"
            >
              评分
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 悬浮效果 -->
      <div class="card-glow"></div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  View, Star, Calendar, House, StarFilled 
} from '@element-plus/icons-vue'

const props = defineProps({
  book: {
    type: Object,
    required: true
  },
  enhanced: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

const displayRating = computed(() => {
  return props.book.avgRating || 0
})

const isPopular = computed(() => {
  return props.book.avgRating > 4.0 && props.book.ratingCount > 50
})

const isNew = computed(() => {
  const currentYear = new Date().getFullYear()
  return props.book.year >= currentYear - 2
})

const ratingColors = ['#FF6B6B', '#FFA726', '#FFD54F']

const formatRating = (rating) => {
  return rating ? Number(rating).toFixed(1) : '0.0'
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const goToDetail = () => {
  router.push(`/books/${props.book.bookId}`)
}

const handleImageError = (event) => {
  event.target.src = '/default-book.jpg'
}

const handleQuickAction = (action) => {
  switch (action) {
    case 'favorite':
      ElMessage.success('已添加到收藏')
      break
    case 'rate':
      ElMessage.info('评分功能即将开放')
      break
  }
}
</script>

<style scoped>
/* 苹果风格图书卡片 */
.book-card-wrapper {
  position: relative;
  height: 100%;
}

.book-card {
  cursor: pointer;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.06);
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: rgba(0, 122, 255, 0.2);
}

.book-card.enhanced {
  background: white;
}

.book-card.enhanced:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

/* 卡片发光效果 */
.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent, rgba(0, 122, 255, 0.05), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 1;
}

.book-card:hover .card-glow {
  opacity: 1;
}

/* 图书图片容器 */
.book-image-container {
  position: relative;
  text-align: center;
  margin-bottom: 16px;
  padding: 20px 20px 10px;
}

.book-image {
  position: relative;
  display: inline-block;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.book-image:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.book-cover {
  width: 140px;
  height: 180px;
  object-fit: cover;
  display: block;
  transition: all 0.3s ease;
}

/* 图片悬浮遮罩 */
.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.8), rgba(88, 86, 214, 0.8));
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
}

.book-image:hover .image-overlay {
  opacity: 1;
}

.view-icon {
  font-size: 2rem;
  color: white;
  transform: scale(0.8);
  transition: transform 0.3s ease;
}

.image-overlay:hover .view-icon {
  transform: scale(1);
}

/* 标签样式 */
.popular-badge,
.new-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 3px;
  z-index: 2;
}

.popular-badge {
  background: #ff9500;
  color: white;
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.3);
}

.new-badge {
  background: #34c759;
  color: white;
  box-shadow: 0 2px 8px rgba(52, 199, 89, 0.3);
}

/* 图书信息 */
.book-info {
  padding: 0 20px 20px;
  position: relative;
  z-index: 2;
}

.book-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1d1d1f;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 44px;
  line-height: 1.4;
  transition: color 0.3s ease;
  letter-spacing: -0.01em;
}

.book-card:hover .book-title {
  color: #007aff;
}

.book-author {
  font-size: 13px;
  color: #86868b;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 400;
}

/* 图书元数据 */
.book-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 8px;
}

.book-year,
.book-publisher {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #86868b;
  background: rgba(0, 0, 0, 0.04);
  padding: 4px 8px;
  border-radius: 6px;
  flex: 1;
  justify-content: center;
  font-weight: 500;
}

.book-year .el-icon,
.book-publisher .el-icon {
  font-size: 12px;
}

/* 评分区域 */
.book-stats {
  margin-top: 12px;
}

.rating-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 6px;
}

.rating-score {
  font-size: 14px;
  font-weight: 600;
  color: #007aff;
  min-width: 30px;
}

.rating-count {
  font-size: 11px;
  color: #86868b;
  text-align: center;
  display: block;
}

/* 增强模式下的操作按钮 */
.enhanced-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-buttons .el-button {
  border-radius: 12px;
  font-size: 12px;
  padding: 6px 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  border: none;
}

.action-buttons .el-button--primary {
  background: #007aff;
  color: white;
}

.action-buttons .el-button--primary:hover {
  background: #0056cc;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.action-buttons .el-button:not(.el-button--primary) {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.action-buttons .el-button:not(.el-button--primary):hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-cover {
    width: 120px;
    height: 160px;
  }
  
  .book-title {
    font-size: 14px;
    min-height: 38px;
  }
  
  .book-meta {
    flex-direction: column;
    gap: 6px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

/* 加载状态动画 */
@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

.book-card.loading {
  background: linear-gradient(90deg, #f8f9fa 25%, #e9ecef 50%, #f8f9fa 75%);
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
}
</style>