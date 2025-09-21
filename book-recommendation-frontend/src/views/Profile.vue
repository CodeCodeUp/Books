<template>
  <div class="profile">
    <el-card class="profile-card">
      <template #header>
        <h2>个人中心</h2>
      </template>
      
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" disabled />
        </el-form-item>
        
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="userForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="地理位置">
          <el-input v-model="userForm.location" disabled />
        </el-form-item>
        
        <el-form-item label="年龄">
          <el-input v-model="userForm.age" disabled />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleUpdate">
            更新信息
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { userApi } from '../api/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const userFormRef = ref()
const loading = ref(false)

const userForm = reactive({
  username: '',
  nickname: '',
  email: '',
  location: '',
  age: ''
})

const rules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const loadUserInfo = async () => {
  if (userStore.user) {
    const user = userStore.user
    userForm.username = user.username || ''
    userForm.nickname = user.nickname || ''
    userForm.email = user.email || ''
    userForm.location = user.location || ''
    userForm.age = user.age || ''
  }
}

const handleUpdate = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userApi.updateUserInfo(userStore.user.userId, userForm.nickname, userForm.email)
        
        // 更新本地用户信息
        userStore.setUser({
          ...userStore.user,
          nickname: userForm.nickname,
          email: userForm.email
        })
        
        ElMessage.success('更新成功')
      } catch (error) {
        ElMessage.error('更新失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const resetForm = () => {
  loadUserInfo()
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile {
  max-width: 600px;
  margin: 0 auto;
}

.profile-card {
  margin-top: 20px;
}
</style>