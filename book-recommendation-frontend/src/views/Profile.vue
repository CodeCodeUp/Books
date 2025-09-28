<template>
  <div class="profile-container">
    <!-- 页面头部 -->
    <div class="profile-header" data-aos="fade-down">
      <div class="header-content">
        <div class="user-avatar-section">
          <el-avatar :size="80" class="user-avatar">
            <el-icon><UserFilled /></el-icon>
          </el-avatar>
          <div class="user-basic-info">
            <h1 class="username">{{ userForm.username }}</h1>
            <p class="user-status">{{ profileCompleteness }}% 资料完整度</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="profile-content">
      <!-- 资料完善提示 -->
      <div 
        v-if="showIncompleteAlert" 
        class="alert-card" 
        data-aos="fade-up"
      >
        <div class="alert-content">
          <el-icon class="alert-icon"><InfoFilled /></el-icon>
          <div class="alert-text">
            <h3>完善您的资料</h3>
            <p>完整的个人资料有助于为您提供更精准的图书推荐</p>
          </div>
        </div>
      </div>

      <!-- 个人信息表单 -->
      <div class="form-section" data-aos="fade-up" data-aos-delay="100">
        <div class="section-header">
          <h2 class="section-title">个人信息</h2>
          <p class="section-subtitle">管理您的个人资料和偏好设置</p>
        </div>

        <div class="form-card">
          <el-form 
            :model="userForm" 
            :rules="rules" 
            ref="userFormRef" 
            label-position="top"
            class="profile-form"
          >
            <div class="form-grid">
              <!-- 基本信息 -->
              <div class="form-section-group">
                <h3 class="group-title">基本信息</h3>
                
                <el-form-item label="用户名" class="form-item">
                  <el-input 
                    v-model="userForm.username" 
                    disabled 
                    class="form-input"
                  >
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                
                <el-form-item label="昵称" prop="nickname" class="form-item">
                  <el-input 
                    v-model="userForm.nickname" 
                    placeholder="请输入您的昵称"
                    class="form-input"
                  >
                    <template #prefix>
                      <el-icon><UserFilled /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                
                <el-form-item label="邮箱" prop="email" class="form-item">
                  <el-input 
                    v-model="userForm.email" 
                    placeholder="请输入您的邮箱地址"
                    class="form-input"
                  >
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </div>

              <!-- 个性化信息 -->
              <div class="form-section-group">
                <h3 class="group-title">个性化信息</h3>
                <p class="group-description">这些信息将帮助我们为您推荐更合适的图书</p>
                
                <el-form-item label="所在地区" prop="location" class="form-item">
                  <el-input 
                    v-model="userForm.location" 
                    placeholder="请输入您的所在地区"
                    class="form-input"
                  >
                    <template #prefix>
                      <el-icon><LocationFilled /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                
                <el-form-item label="年龄" prop="age" class="form-item">
                  <el-input-number 
                    v-model="userForm.age" 
                    :min="1" 
                    :max="120"
                    placeholder="请输入您的年龄"
                    class="form-input age-input"
                    controls-position="right"
                  />
                </el-form-item>
                
                <el-form-item label="国家/地区" prop="country" class="form-item">
                  <el-select 
                    v-model="userForm.country" 
                    placeholder="请选择您的国家/地区"
                    class="form-input"
                    filterable
                  >
                    <template #prefix>
                      <el-icon><Flag /></el-icon>
                    </template>
                    <el-option label="中国" value="中国" />
                    <el-option label="美国" value="美国" />
                    <el-option label="英国" value="英国" />
                    <el-option label="日本" value="日本" />
                    <el-option label="韩国" value="韩国" />
                    <el-option label="德国" value="德国" />
                    <el-option label="法国" value="法国" />
                    <el-option label="加拿大" value="加拿大" />
                    <el-option label="澳大利亚" value="澳大利亚" />
                    <el-option label="其他" value="其他" />
                  </el-select>
                </el-form-item>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="form-actions">
              <button 
                type="button"
                :disabled="loading"
                @click="handleUpdate"
                class="btn-primary"
              >
                <el-icon v-if="!loading"><Check /></el-icon>
                <el-icon v-else class="loading-icon"><Loading /></el-icon>
                {{ loading ? '保存中...' : '保存更改' }}
              </button>
              <button 
                type="button"
                @click="resetForm"
                class="btn-secondary"
              >
                <el-icon><Refresh /></el-icon>
                重置
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/user'
import { ElMessage } from 'element-plus'
import { 
  UserFilled, User, Message, LocationFilled, Flag, 
  InfoFilled, Check, Loading, Refresh
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const userFormRef = ref()
const loading = ref(false)

const userForm = reactive({
  username: '',
  nickname: '',
  email: '',
  location: '',
  age: null,
  country: ''
})

const rules = {
  nickname: [
    { min: 2, max: 20, message: '昵称长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入所在地区', trigger: 'blur' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' },
    { type: 'number', min: 1, max: 120, message: '年龄必须在 1-120 之间', trigger: 'blur' }
  ],
  country: [
    { required: true, message: '请选择国家/地区', trigger: 'change' }
  ]
}

// 计算资料完整度
const profileCompleteness = computed(() => {
  // 只考虑必填字段：location, age, country
  const requiredFields = ['location', 'age', 'country']
  const completedFields = requiredFields.filter(field => {
    const value = userForm[field]
    return value !== null && value !== undefined && value !== ''
  })
  return Math.round((completedFields.length / requiredFields.length) * 100)
})

// 是否显示资料不完整提示
const showIncompleteAlert = computed(() => {
  return !userForm.location || !userForm.age || !userForm.country
})

const loadUserInfo = async () => {
  if (userStore.user) {
    const user = userStore.user
    userForm.username = user.username || ''
    userForm.nickname = user.nickname || ''
    userForm.email = user.email || ''
    userForm.location = user.location || ''
    userForm.age = user.age || null
    userForm.country = user.country || ''
  }
}

const loadUserRatings = async () => {
  if (!userStore.user) return
  
  ratingsLoading.value = true
  try {
    const response = await userApi.getUserRatings(userStore.user.userId)
    userRatings.value = response.data || []
  } catch (error) {
    console.log('加载评分历史失败')
    userRatings.value = []
  } finally {
    ratingsLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const handleImageError = (event) => {
  event.target.src = '/default-book.jpg'
}

const viewAllRatings = () => {
  // 可以跳转到专门的评分历史页面或展开显示
  ElMessage.info('查看全部评分功能可以后续扩展')
}

const handleUpdate = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用API更新用户信息
        await userApi.updateUserInfo(userStore.user.userId, {
          nickname: userForm.nickname,
          email: userForm.email,
          location: userForm.location,
          age: userForm.age,
          country: userForm.country
        })
        
        // 更新本地用户信息
        userStore.setUser({
          ...userStore.user,
          nickname: userForm.nickname,
          email: userForm.email,
          location: userForm.location,
          age: userForm.age,
          country: userForm.country
        })
        
        ElMessage.success({
          message: '个人信息更新成功！',
          duration: 3000,
          showClose: true
        })
        
        // 如果资料现在完整了，给予提示
        if (profileCompleteness.value === 100) {
          setTimeout(() => {
            ElMessage.info({
              message: '太棒了！您的资料已完善，现在可以享受更精准的图书推荐了',
              duration: 4000,
              showClose: true
            })
          }, 1000)
        }
        
      } catch (error) {
        ElMessage.error({
          message: '更新失败，请重试',
          duration: 3000,
          showClose: true
        })
      } finally {
        loading.value = false
      }
    }
  })
}

const resetForm = () => {
  loadUserInfo()
  ElMessage.info('表单已重置')
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
/* 苹果风格个人中心 */
.profile-container {
  min-height: 100vh;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 页面头部 */
.profile-header {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  padding: 40px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
}

.user-avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  background: #007aff;
  color: white;
  font-size: 2rem;
  box-shadow: 0 4px 20px rgba(0, 122, 255, 0.2);
}

.user-basic-info {
  flex: 1;
}

.username {
  font-size: 2rem;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.user-status {
  font-size: 1rem;
  color: #86868b;
  margin: 0;
  font-weight: 500;
}

/* 主要内容区域 */
.profile-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 资料完善提示 */
.alert-card {
  background: rgba(0, 122, 255, 0.05);
  border: 1px solid rgba(0, 122, 255, 0.15);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 32px;
}

.alert-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.alert-icon {
  font-size: 1.5rem;
  color: #007aff;
  margin-top: 2px;
}

.alert-text h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 4px 0;
}

.alert-text p {
  font-size: 0.9rem;
  color: #86868b;
  margin: 0;
  line-height: 1.4;
}

/* 表单区域 */
.form-section {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.section-header {
  padding: 32px 32px 0;
  text-align: center;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 1rem;
  color: #86868b;
  margin: 0;
  line-height: 1.4;
}

.form-card {
  padding: 32px;
}

.form-grid {
  display: grid;
  gap: 40px;
}

.form-section-group {
  border-radius: 16px;
  background: #f8f9fa;
  padding: 24px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.group-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  letter-spacing: -0.01em;
}

.group-description {
  font-size: 0.9rem;
  color: #86868b;
  margin: 0 0 24px 0;
  line-height: 1.4;
}

.form-item {
  margin-bottom: 24px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item :deep(.el-form-item__label) {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: white;
  padding: 0 16px;
  height: 48px;
  transition: all 0.2s ease;
  box-shadow: none;
}

.form-input :deep(.el-input__wrapper):hover {
  border-color: #007aff;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #007aff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.form-input :deep(.el-input__prefix) {
  color: #86868b;
}

.form-input :deep(.el-select__wrapper) {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: white;
  padding: 0 16px;
  height: 48px;
  transition: all 0.2s ease;
  box-shadow: none;
}

.age-input {
  width: 100%;
}

.age-input :deep(.el-input-number__wrapper) {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: white;
  height: 48px;
  transition: all 0.2s ease;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 32px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.btn-primary {
  background: #007aff;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: #0056cc;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-header {
    padding: 24px 16px;
  }
  
  .user-avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .username {
    font-size: 1.5rem;
  }
  
  .profile-content {
    padding: 24px 16px;
  }
  
  .form-card {
    padding: 24px 20px;
  }
  
  .form-section-group {
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-primary,
  .btn-secondary {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .alert-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .alert-icon {
    align-self: flex-start;
  }
}
</style>