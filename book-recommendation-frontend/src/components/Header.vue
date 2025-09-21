<template>
  <div class="header-container">
    <div class="logo">
      <router-link to="/">图书推荐系统</router-link>
    </div>
    
    <div class="nav-menu">
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
        router
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/books">图书列表</el-menu-item>
        <el-menu-item index="/recommendations" v-if="userStore.isLoggedIn">推荐</el-menu-item>
      </el-menu>
    </div>
    
    <div class="user-actions">
      <template v-if="userStore.isLoggedIn">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ userStore.user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      
      <template v-else>
        <el-button type="primary" @click="$router.push('/login')">登录</el-button>
        <el-button @click="$router.push('/register')">注册</el-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/')
  }
}
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 20px;
}

.logo {
  margin-right: 20px;
}

.logo a {
  color: white;
  text-decoration: none;
  font-size: 20px;
  font-weight: bold;
}

.nav-menu {
  flex: 1;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>