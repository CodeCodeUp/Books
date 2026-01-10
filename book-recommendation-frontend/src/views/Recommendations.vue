<template>
  <div class="recommendations">
    <div class="header-section">
      <h1>个性化推荐</h1>
      <p>基于您的阅读历史和相似用户偏好为您推荐感兴趣的图书</p>
    </div>
    
    <!-- 服务状态检查 -->
    <el-alert
      v-if="!serviceHealthy"
      title="推荐服务暂时不可用"
      type="warning"
      description="算法服务正在启动中，请稍后刷新页面"
      show-icon
      :closable="false"
    />
    
    <!-- 推荐设置 -->
    <el-card class="settings-card" v-if="serviceHealthy">
      <template #header>
        <h3>推荐设置</h3>
      </template>
      
      <el-form :inline="true" :model="recommendForm" class="recommend-form">
        <el-form-item label="推荐数量">
          <el-select
            v-model="recommendForm.topN"
            placeholder="请选择推荐数量"
            style="width: 120px"
          >
            <el-option label="5本" :value="5" />
            <el-option label="10本" :value="10" />
            <el-option label="15本" :value="15" />
            <el-option label="20本" :value="20" />
          </el-select>
        </el-form-item>

        <el-form-item label="最低评分">
          <el-select
            v-model="recommendForm.minRating"
            placeholder="请选择最低评分"
            style="width: 140px"
          >
            <el-option label="2.0分以上" :value="2.0" />
            <el-option label="3.0分以上" :value="3.0" />
            <el-option label="3.5分以上" :value="3.5" />
            <el-option label="4.0分以上" :value="4.0" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="resetRecommendations"
            :loading="loading"
            icon="Refresh"
          >
            生成推荐
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 推荐结果 -->
    <div v-if="recommendations.length > 0 || loading" class="recommendations-section">
      <div class="section-header">
        <h2>为您推荐</h2>
        <div class="header-actions">
          <el-button
            v-if="!loading && total > recommendForm.topN"
            type="primary"
            size="small"
            @click="loadNextPage"
            class="tactile-btn"
          >
            <el-icon :class="{ 'is-rotating': loading }"><RefreshRight /></el-icon>
            换一批
          </el-button>
        </div>
      </div>

      <Transition name="fade" mode="out-in">
        <div v-if="loading" class="loading-container" key="loading">
          <HourglassLoader text="正在生成个性化推荐..." size="72px" />
        </div>
        <div
          v-else
          class="book-grid"
          :key="currentOffset"
        >
          <div
            v-for="(item, index) in recommendations"
            :key="item.bookId"
            class="recommendation-item"
            :style="{ animationDelay: `${index * 0.05}s` }"
          >
            <BookCard :book="item" />
          </div>
        </div>
      </Transition>
    </div>
    
    <!-- 相似用户信息（暂时隐藏） -->
    <!-- 
    <el-card v-if="similarUsers.length > 0 && !loading" class="similar-users-card">
      <template #header>
        <h3>与您兴趣相似的用户</h3>
      </template>
      
      <div class="similar-users-list">
        <div 
          v-for="user in similarUsers.slice(0, 5)" 
          :key="user.user_id"
          class="similar-user-item"
        >
          <el-avatar :size="40">{{ user.user_id }}</el-avatar>
          <div class="user-info">
            <span class="user-id">用户 {{ user.user_id }}</span>
            <span class="similarity">相似度: {{ (user.similarity * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </el-card>
    -->
    
    <!-- 空状态 -->
    <el-empty 
      v-if="!loading && recommendations.length === 0 && serviceHealthy" 
      description="暂无推荐结果，请先对一些图书进行评分"
    >
      <el-button type="primary" @click="$router.push('/books')">去图书列表评分</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { recommendApi } from '../api/recommendation'
import BookCard from '../components/BookCard.vue'
import HourglassLoader from '../components/HourglassLoader.vue'
import { ElMessage } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'

const userStore = useUserStore()

const loading = ref(false)
const serviceHealthy = ref(true)
const recommendations = ref([])
const similarUsers = ref([])
const algorithmInfo = ref('')

// 分页相关状态
const currentOffset = ref(0)
const total = ref(0)

const recommendForm = reactive({
  topN: 10,
  minRating: 3.0
})

const checkServiceHealth = async () => {
  try {
    const response = await recommendApi.checkHealth()
    serviceHealthy.value = response.data
  } catch (error) {
    serviceHealthy.value = false
    ElMessage.warning('推荐服务暂时不可用')
  }
}

const generateRecommendations = async (offset = 0) => {
  if (!userStore.user) {
    ElMessage.error('请先登录')
    return
  }

  loading.value = true
  try {
    const response = await recommendApi.getUserBasedRecommendations(
      userStore.user.userId,
      recommendForm.topN,
      offset,
      recommendForm.minRating
    )

    recommendations.value = response.data.recommendations || []
    total.value = response.data.total || 0
    currentOffset.value = offset
    algorithmInfo.value = response.data.algorithm_info?.name || '混合推荐算法'
    similarUsers.value = []

  } catch (error) {
    ElMessage.error('生成推荐失败，请检查算法服务是否运行')
  } finally {
    loading.value = false
  }
}

// 换一批：自动循环
const loadNextPage = () => {
  let nextOffset = currentOffset.value + recommendForm.topN
  // 超过总数则从头开始
  if (nextOffset >= total.value) {
    nextOffset = 0
  }
  generateRecommendations(nextOffset)
}

// 从头开始
const resetRecommendations = () => {
  generateRecommendations(0)
}

onMounted(() => {
  checkServiceHealth()
  if (userStore.isLoggedIn) {
    generateRecommendations(0)
  }
})
</script>

<style scoped>
.recommendations {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h1 {
  color: #333;
  margin-bottom: 10px;
}

.header-section p {
  color: #666;
  font-size: 16px;
}

.settings-card {
  margin-bottom: 30px;
}

.recommend-form {
  display: flex;
  align-items: center;
  gap: 20px;
}

.recommendations-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.section-header h2 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 触觉反馈按钮 */
.tactile-btn {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.tactile-btn:active {
  transform: scale(0.95);
}

.tactile-btn:hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.tactile-btn .el-icon {
  margin-right: 4px;
  transition: transform 0.3s ease;
}

.tactile-btn .el-icon.is-rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

/* 加载容器 */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(20px);
  border-radius: 20px;
}

/* 卡片入场动画 */
.recommendation-item {
  position: relative;
  animation: slideUp 0.4s ease forwards;
  opacity: 0;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.recommendation-info {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 12px;
}

.predicted-rating,
.recommendation-reason {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 5px 0;
  color: #666;
}

.similar-users-card {
  margin-bottom: 30px;
}

.similar-users-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.similar-user-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  min-width: 200px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-id {
  font-weight: bold;
  color: #333;
}

.similarity {
  font-size: 12px;
  color: #666;
}
</style>