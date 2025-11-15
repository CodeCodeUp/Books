<template>
  <div class="complete-profile-container">
    <!-- 步骤1：填写年龄 -->
    <div v-if="currentStep === 1" class="step-container">
      <div class="step-content">
        <div class="header">
          <h1 class="title">告诉我们您的年龄</h1>
          <p class="subtitle">这将帮助我们为您推荐更合适的图书</p>
        </div>

        <el-form
          :model="profileForm"
          :rules="rules"
          ref="profileFormRef"
          class="age-form"
        >
          <el-form-item prop="age" class="age-item">
            <el-input-number
              v-model="profileForm.age"
              :min="1"
              :max="120"
              placeholder="请输入年龄"
              class="age-input"
              controls-position="right"
            />
          </el-form-item>

          <div class="button-group">
            <button
              type="button"
              @click="nextStep"
              :disabled="!profileForm.age"
              class="btn-primary"
            >
              下一步
            </button>
            <button
              type="button"
              @click="skipToLogin"
              class="btn-skip"
            >
              暂时跳过
            </button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 步骤2：选择兴趣 -->
    <div v-if="currentStep === 2" class="interest-step">
      <InterestSelector
        title="选择您感兴趣的图书类型"
        subtitle="我们将根据您的兴趣为您推荐精彩图书"
        :min-selection="0"
        :random-count="5"
        confirm-text="完成"
        skip-text="暂时跳过"
        :allow-skip="true"
        :initial-selected="[]"
        @confirm="handleInterestConfirm"
        @skip="handleInterestSkip"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/user'
import { ElMessage } from 'element-plus'
import InterestSelector from '../components/InterestSelector.vue'

const router = useRouter()
const userStore = useUserStore()
const profileFormRef = ref()
const currentStep = ref(1)

const profileForm = reactive({
  age: null
})

const rules = {
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' },
    { type: 'number', min: 1, max: 120, message: '年龄必须在 1-120 之间', trigger: 'blur' }
  ]
}

const nextStep = async () => {
  const valid = await profileFormRef.value?.validate().catch(() => false)
  if (!valid) return

  // 保存年龄
  try {
    await userApi.updateUserInfo(userStore.user.userId, {
      age: profileForm.age
    })

    // 更新用户信息
    userStore.setUser({
      ...userStore.user,
      age: profileForm.age
    })

    currentStep.value = 2
  } catch (error) {
    ElMessage.error('保存年龄失败，请重试')
  }
}

const handleInterestConfirm = async (themeIds) => {
  try {
    // 保存用户兴趣
    await userApi.saveUserInterests(userStore.user.userId, themeIds)

    ElMessage.success({
      message: '资料完善成功！欢迎使用图书推荐系统',
      duration: 2000
    })

    setTimeout(() => {
      router.push('/')
    }, 1000)
  } catch (error) {
    ElMessage.error('保存兴趣失败')
  }
}

const handleInterestSkip = () => {
  ElMessage.info('您可以稍后在个人中心设置兴趣偏好')
  setTimeout(() => {
    router.push('/')
  }, 1000)
}

const skipToLogin = () => {
  ElMessage.info('您可以稍后在个人中心完善资料')
  router.push('/')
}

onMounted(() => {
  // 检查用户是否已登录
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先注册账号')
    router.push('/register')
  }
})
</script>

<style scoped>
.complete-profile-container {
  min-height: 100vh;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 步骤1: 年龄填写 */
.step-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.step-content {
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 24px;
  padding: 60px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.header {
  text-align: center;
  margin-bottom: 48px;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 16px 0;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 1rem;
  color: #86868b;
  margin: 0;
  line-height: 1.5;
}

.age-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.age-item {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 0;
}

.age-input {
  width: 240px;
}

.age-input :deep(.el-input-number__wrapper) {
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #f8f9fa;
  height: 72px;
  font-size: 2rem;
  transition: all 0.2s ease;
  box-shadow: none;
}

.age-input :deep(.el-input-number__wrapper):hover {
  border-color: #34c759;
  background: #ffffff;
}

.age-input :deep(.el-input__inner) {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: #1d1d1f;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 400px;
}

.btn-primary {
  width: 100%;
  height: 56px;
  border-radius: 16px;
  background: #34c759;
  border: none;
  font-size: 18px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(52, 199, 89, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: #30b47a;
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(52, 199, 89, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-skip {
  width: 100%;
  height: 48px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 16px;
  font-weight: 500;
  color: #86868b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-skip:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #1d1d1f;
}

/* 步骤2: 兴趣选择 - PC布局 */
.interest-step {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #fafafa;
}

/* 响应式 */
@media (max-width: 768px) {
  .step-content {
    padding: 40px 24px;
  }

  .title {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 0.95rem;
  }

  .age-input {
    width: 200px;
  }

  .age-input :deep(.el-input-number__wrapper) {
    height: 64px;
    font-size: 1.75rem;
  }

  .age-input :deep(.el-input__inner) {
    font-size: 1.75rem;
  }
}
</style>
