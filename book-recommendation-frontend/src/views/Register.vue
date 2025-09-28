<template>
  <div class="auth-container">
    <!-- 主要内容 -->
    <div class="auth-content">
      <div class="auth-wrapper">
        <!-- 左侧装饰区域 -->
        <div class="auth-left">
          <div class="welcome-section">
            <h1 class="welcome-title">开始阅读</h1>
            <p class="welcome-subtitle">注册账户，开启个性化阅读之旅</p>
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
        
        <!-- 右侧注册表单 -->
        <div class="auth-right">
          <div class="auth-card">
            <div class="card-header">
              <div class="logo-section">
                <el-icon class="logo-icon"><Reading /></el-icon>
                <h2 class="auth-title">用户注册</h2>
              </div>
              <p class="auth-subtitle">创建您的图书推荐系统账户</p>
            </div>
            
            <el-form 
              :model="registerForm" 
              :rules="rules" 
              ref="registerFormRef"
              class="auth-form"
              size="large"
            >
              <el-form-item prop="username" class="form-item">
                <el-input
                  v-model="registerForm.username"
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
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  class="form-input"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item prop="confirmPassword" class="form-item">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请确认密码"
                  show-password
                  class="form-input"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item class="form-item">
                <button 
                  type="button"
                  :disabled="loading"
                  @click="handleRegister"
                  class="auth-btn"
                >
                  <span v-if="!loading">立即注册</span>
                  <span v-else>注册中...</span>
                </button>
              </el-form-item>
              
              <div class="auth-footer">
                <span class="footer-text">已有账号？</span>
                <router-link to="/login" class="register-link">
                  立即登录
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { userApi } from '../api/user'
import { ElMessage } from 'element-plus'
import { 
  User, Lock, Star, CollectionTag, UserFilled, Reading 
} from '@element-plus/icons-vue'

const router = useRouter()
const registerFormRef = ref()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userApi.register(registerForm.username, registerForm.password, null)
        
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } catch (error) {
        ElMessage.error('注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
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
  background: linear-gradient(135deg, #34c759 0%, #30b47a 100%);
  border-radius: 24px;
  color: white;
  box-shadow: 0 10px 30px rgba(52, 199, 89, 0.3);
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
  color: #34c759;
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
  border-color: rgba(52, 199, 89, 0.3);
  background: #ffffff;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #34c759;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(52, 199, 89, 0.1);
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

/* 认证按钮 */
.auth-btn {
  width: 100%;
  height: 52px;
  border-radius: 12px;
  background: #34c759;
  border: none;
  font-size: 17px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(52, 199, 89, 0.3);
}

.auth-btn:hover:not(:disabled) {
  background: #30b47a;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(52, 199, 89, 0.4);
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
  color: #34c759;
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
  transition: all 0.2s ease;
}

.register-link:hover {
  color: #30b47a;
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