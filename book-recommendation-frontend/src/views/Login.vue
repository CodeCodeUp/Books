<template>
  <div class="auth-container">
    <!-- 主要内容 -->
    <div class="auth-content">
      <div class="auth-wrapper">
        <!-- 左侧装饰区域 -->
        <div class="auth-left">
          <div class="welcome-section">
            <h1 class="welcome-title">欢迎回来</h1>
            <p class="welcome-subtitle">探索知识海洋，发现阅读之美</p>
            <div class="feature-list">
              <div class="feature-item">
                <el-icon class="feature-icon"><Star /></el-icon>
                <span>智能推荐算法</span>
              </div>
              <div class="feature-item">
                <el-icon class="feature-icon"><CollectionTag /></el-icon>
                <span>27万+精选图书</span>
              </div>
              <div class="feature-item">
                <el-icon class="feature-icon"><UserFilled /></el-icon>
                <span>个性化阅读体验</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧登录表单 -->
        <div class="auth-right">
          <div class="auth-card">
            <div class="card-header">
              <div class="logo-section">
                <el-icon class="logo-icon"><Reading /></el-icon>
                <h2 class="auth-title">用户登录</h2>
              </div>
              <p class="auth-subtitle">使用您的账户登录到图书推荐系统</p>
            </div>
            
            <el-form 
              :model="loginForm" 
              :rules="rules" 
              ref="loginFormRef" 
              @submit.prevent="handleLogin"
              class="auth-form"
              size="large"
            >
              <el-form-item prop="username" class="form-item">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  class="form-input"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item prop="password" class="form-item">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  class="form-input"
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item class="form-item">
                <div class="form-options">
                  <el-checkbox v-model="rememberMe" class="remember-checkbox">
                    记住我
                  </el-checkbox>
                  <el-link type="primary" class="forgot-link">
                    忘记密码？
                  </el-link>
                </div>
              </el-form-item>
              
              <el-form-item class="form-item">
                <button 
                  type="button"
                  :disabled="loading"
                  @click="handleLogin"
                  class="auth-btn"
                >
                  <span v-if="!loading">立即登录</span>
                  <span v-else>登录中...</span>
                </button>
              </el-form-item>
              
              <div class="auth-footer">
                <span class="footer-text">还没有账号？</span>
                <router-link to="/register" class="register-link">
                  立即注册
                </router-link>
              </div>
            </el-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/user'
import { ElMessage } from 'element-plus'
import { 
  User, Lock, Star, CollectionTag, UserFilled, Reading
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref()
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await userApi.login(loginForm.username, loginForm.password)
        
        // 从后端响应中获取用户信息和token
        const { user, token } = response.data
        
        userStore.setUser(user)
        userStore.setToken(token)
        
        ElMessage.success({
          message: `欢迎回来，${user.username}！`,
          duration: 3000,
          showClose: true
        })
        
        setTimeout(() => {
          router.push('/')
        }, 1000)
        
      } catch (error) {
        ElMessage.error({
          message: '登录失败，请检查用户名和密码',
          duration: 3000,
          showClose: true
        })
      } finally {
        loading.value = false
      }
    }
  })
}



onMounted(() => {
  // 移除页面进入动画
})
</script>

<style scoped>
/* 苹果风格认证页面 */
.auth-container {
  min-height: 100vh;
  position: relative;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 主要内容 */
.auth-content {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1200px;
  width: 100%;
  gap: 60px;
  align-items: center;
}

/* 左侧装饰区域 */
.auth-left {
  padding: 40px;
  background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
  border-radius: 24px;
  color: white;
  box-shadow: 0 10px 30px rgba(0, 122, 255, 0.3);
}

.welcome-section {
  text-align: center;
}

.welcome-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 20px 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.welcome-subtitle {
  font-size: 1.125rem;
  opacity: 0.9;
  margin: 0 0 40px 0;
  font-weight: 400;
  line-height: 1.4;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.15);
  padding: 12px 20px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  min-width: 240px;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.25rem;
  color: #ffffff;
}

.feature-item span {
  font-size: 0.9rem;
  font-weight: 500;
}

/* 右侧认证表单 */
.auth-right {
  display: flex;
  justify-content: center;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 2.5rem;
  color: #007aff;
}

.auth-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.02em;
}

.auth-subtitle {
  font-size: 0.9rem;
  color: #86868b;
  margin: 0;
  font-weight: 400;
  line-height: 1.4;
}

/* 表单样式 */
.auth-form {
  margin-top: 24px;
}

.form-item {
  margin-bottom: 20px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: none;
  background: #f8f9fa;
  padding: 16px;
  height: 52px;
  transition: all 0.2s ease;
}

.form-input :deep(.el-input__wrapper):hover {
  border-color: rgba(0, 122, 255, 0.3);
  background: #ffffff;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #007aff;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.input-icon {
  color: #86868b;
  font-size: 1.1rem;
}

.form-input :deep(.el-input__inner) {
  font-size: 16px;
  color: #1d1d1f;
  font-weight: 400;
}

.form-input :deep(.el-input__inner::placeholder) {
  color: #86868b;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-checkbox :deep(.el-checkbox__label) {
  color: #1d1d1f;
  font-size: 14px;
  font-weight: 400;
}

.forgot-link {
  font-size: 14px;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

/* 认证按钮 */
.auth-btn {
  width: 100%;
  height: 52px;
  border-radius: 12px;
  background: #007aff;
  border: none;
  font-size: 17px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.3);
}

.auth-btn:hover:not(:disabled) {
  background: #0056cc;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

.auth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 页脚 */
.auth-footer {
  text-align: center;
  margin-top: 24px;
}

.footer-text {
  color: #86868b;
  font-size: 14px;
  font-weight: 400;
}

.register-link {
  color: #007aff;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
  transition: all 0.2s ease;
}

.register-link:hover {
  color: #0056cc;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .auth-wrapper {
    grid-template-columns: 1fr;
    gap: 40px;
    max-width: 500px;
  }
  
  .auth-left {
    padding: 32px;
    order: 2;
  }
  
  .welcome-title {
    font-size: 2.5rem;
  }
  
  .feature-list {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .feature-item {
    min-width: 200px;
    padding: 10px 16px;
  }
}

@media (max-width: 768px) {
  .auth-content {
    padding: 16px;
  }
  
  .auth-card {
    padding: 32px 24px;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .feature-list {
    flex-direction: column;
  }
  
  .feature-item {
    min-width: auto;
    width: 100%;
  }
  
  .form-input :deep(.el-input__wrapper) {
    height: 48px;
    padding: 14px;
  }
  
  .auth-btn {
    height: 48px;
  }
}

@media (max-width: 480px) {
  .auth-card {
    margin: 0 8px;
    padding: 24px 20px;
  }
  
  .welcome-title {
    font-size: 1.8rem;
  }
  
  .feature-item {
    padding: 10px 16px;
    font-size: 0.85rem;
  }
  
  .auth-title {
    font-size: 1.5rem;
  }
}
</style>