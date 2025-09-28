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
          <el-select v-model="recommendForm.topN" placeholder="选择推荐数量">
            <el-option label="5本" :value="5" />
            <el-option label="10本" :value="10" />
            <el-option label="15本" :value="15" />
            <el-option label="20本" :value="20" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="最低评分">
          <el-select v-model="recommendForm.minRating" placeholder="最低评分">
            <el-option label="2.0分以上" :value="2.0" />
            <el-option label="3.0分以上" :value="3.0" />
            <el-option label="3.5分以上" :value="3.5" />
            <el-option label="4.0分以上" :value="4.0" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="generateRecommendations"
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
        <el-tag type="info" v-if="!loading">{{ algorithmInfo }}</el-tag>
      </div>
      
      <div class="book-grid" v-loading="loading" element-loading-text="正在生成个性化推荐...">
        <div 
          v-for="item in recommendations" 
          :key="item.bookId"
          class="recommendation-item"
        >
          <BookCard :book="item" :enhanced="true" />
        </div>
      </div>
    </div>
    
    <!-- 相似用户信息 -->
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
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const loading = ref(false)
const serviceHealthy = ref(true)
const recommendations = ref([])
const similarUsers = ref([])
const algorithmInfo = ref('')

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

const generateRecommendations = async () => {
  if (!userStore.user) {
    ElMessage.error('请先登录')
    return
  }
  
  loading.value = true
  try {
    // 生成推荐
    const response = await recommendApi.getUserBasedRecommendations(
      userStore.user.userId,
      recommendForm.topN,
      recommendForm.minRating
    )
    
    recommendations.value = response.data.recommendations || []
    algorithmInfo.value = response.data.algorithm_info?.name || '混合推荐算法'
    
    // 只有当推荐结果中包含协同过滤算法时才获取相似用户
    const hasCollaborativeResults = recommendations.value.some(rec => 
      rec.algorithm === 'user_based_cf' || rec.algorithm === 'hybrid'
    )
    
    if (hasCollaborativeResults) {
      try {
        const similarResponse = await recommendApi.getSimilarUsers(userStore.user.userId, 10)
        similarUsers.value = similarResponse.data.similar_users || []
      } catch (error) {
        console.log('获取相似用户失败，可能用户无评分历史')
        similarUsers.value = []
      }
    } else {
      similarUsers.value = []
    }
    
    ElMessage.success(`成功生成${recommendations.value.length}个推荐`)
    
  } catch (error) {
    ElMessage.error('生成推荐失败，请检查算法服务是否运行')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkServiceHealth()
  if (userStore.isLoggedIn) {
    generateRecommendations()
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
}

.section-header h2 {
  color: #333;
  margin: 0;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.recommendation-item {
  position: relative;
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