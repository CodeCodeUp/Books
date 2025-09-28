<template>
  <div class="header-container">
    <div class="header-content">
      <!-- Logo区域 -->
      <div class="logo-section">
        <router-link to="/" class="logo-link">
          <el-icon class="logo-icon"><Reading /></el-icon>
          <span class="logo-text">智能图书推荐</span>
        </router-link>
      </div>
      
      <!-- 导航菜单 -->
      <div class="nav-menu">
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          background-color="transparent"
          text-color="#1d1d1f"
          active-text-color="#007aff"
          :ellipsis="false"
          class="nav-menu-items"
          router
        >
          <el-menu-item index="/" class="nav-item">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/books" class="nav-item">
            <el-icon><Collection /></el-icon>
            <span>图书库</span>
          </el-menu-item>
          <el-menu-item 
            index="/recommendations" 
            v-if="userStore.isLoggedIn" 
            class="nav-item"
          >
            <el-icon><Star /></el-icon>
            <span>推荐</span>
          </el-menu-item>
        </el-menu>
      </div>
      
      <!-- 用户操作区域 -->
      <div class="user-actions">
        <template v-if="userStore.isLoggedIn">
          <!-- 用户下拉菜单 -->
          <el-dropdown @command="handleCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar class="user-avatar" :size="35">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown-menu">
                <el-dropdown-item command="profile" class="dropdown-item">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="my-ratings" class="dropdown-item">
                  <el-icon><Star /></el-icon>
                  我的评分
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" class="dropdown-item logout-item">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        
        <template v-else>
          <div class="auth-buttons">
            <el-button 
              class="auth-btn login-btn" 
              @click="$router.push('/login')"
            >
              <el-icon><User /></el-icon>
              登录
            </el-button>
            <el-button 
              type="primary" 
              class="auth-btn register-btn" 
              @click="$router.push('/register')"
            >
              <el-icon><UserFilled /></el-icon>
              注册
            </el-button>
          </div>
        </template>
      </div>
      
      <!-- 移动端菜单按钮 -->
      <div class="mobile-menu-btn" @click="toggleMobileMenu">
        <el-icon><Menu /></el-icon>
      </div>
    </div>
    
    <!-- 移动端抽屉菜单 -->
    <el-drawer
      v-model="mobileMenuVisible"
      direction="rtl"
      :with-header="false"
      size="280px"
      class="mobile-drawer"
    >
      <div class="mobile-menu-content">
        <div class="mobile-logo">
          <el-icon class="mobile-logo-icon"><Reading /></el-icon>
          <span class="mobile-logo-text">智能图书推荐</span>
        </div>
        
        <div class="mobile-nav">
          <div 
            v-for="item in navItems" 
            :key="item.path"
            @click="handleMobileNav(item.path)"
            :class="['mobile-nav-item', { active: activeMenu === item.path }]"
          >
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <span>{{ item.text }}</span>
          </div>
        </div>
        
        <div class="mobile-user-section" v-if="userStore.isLoggedIn">
          <div class="mobile-user-info">
            <el-avatar :size="50">
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
            <span class="mobile-username">{{ userStore.user?.username }}</span>
          </div>
          
          <div class="mobile-user-actions">
            <el-button @click="handleCommand('profile')" text>
              <el-icon><User /></el-icon>
              个人中心
            </el-button>
            <el-button @click="handleCommand('my-ratings')" text>
              <el-icon><Star /></el-icon>
              我的评分
            </el-button>
            <el-button @click="handleCommand('logout')" text type="danger">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </div>
        </div>
        
        <div class="mobile-auth-section" v-else>
          <el-button 
            type="primary" 
            @click="$router.push('/login')"
            class="mobile-auth-btn"
          >
            立即登录
          </el-button>
          <el-button 
            @click="$router.push('/register')"
            class="mobile-auth-btn"
          >
            注册账号
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { 
  Reading, House, Collection, Star, User, UserFilled, 
  ArrowDown, SwitchButton, Menu 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const mobileMenuVisible = ref(false)

const activeMenu = computed(() => route.path)

const navItems = reactive([
  { path: '/', text: '首页', icon: 'House' },
  { path: '/books', text: '图书库', icon: 'Collection' },
  { path: '/recommendations', text: '推荐', icon: 'Star', requireAuth: true }
])

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'my-ratings':
      router.push('/my-ratings')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('退出登录成功')
      router.push('/')
      break
  }
  mobileMenuVisible.value = false
}

const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

const handleMobileNav = (path) => {
  router.push(path)
  mobileMenuVisible.value = false
}
</script>

<style scoped>
/* 苹果风格导航栏 */
.header-container {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Logo区域 */
.logo-section {
  flex-shrink: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #1d1d1f;
  transition: all 0.2s ease;
}

.logo-link:hover {
  transform: scale(1.02);
  color: #007aff;
}

.logo-icon {
  font-size: 1.75rem;
  color: #007aff;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
  margin: 0 40px;
}

.nav-menu-items {
  border: none;
  background: transparent;
}

.nav-menu-items :deep(.el-menu-item) {
  border: none;
  background: transparent;
  color: #1d1d1f;
  font-weight: 500;
  font-size: 16px;
  margin: 0 4px;
  border-radius: 12px;
  padding: 0 16px;
  height: 40px;
  line-height: 40px;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.nav-menu-items :deep(.el-menu-item):hover {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.nav-menu-items :deep(.el-menu-item.is-active) {
  background: rgba(0, 122, 255, 0.15);
  color: #007aff;
  font-weight: 600;
}

.nav-item :deep(.el-icon) {
  margin-right: 6px;
  font-size: 16px;
}

/* 用户操作区域 */
.user-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* 通知按钮 */
.notification-btn {
  position: relative;
}

.action-btn {
  background: rgba(0, 0, 0, 0.04);
  border: none;
  color: #1d1d1f;
  width: 36px;
  height: 36px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: scale(1.05);
}

.notification-badge :deep(.el-badge__content) {
  background: #ff3b30;
  border: 2px solid white;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  line-height: 12px;
}

/* 用户信息下拉 */
.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  color: #1d1d1f;
}

.user-info:hover {
  background: rgba(0, 0, 0, 0.08);
}

.user-avatar {
  background: #007aff;
  color: white;
  font-weight: 600;
}

.username {
  font-weight: 500;
  font-size: 14px;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 12px;
  transition: transform 0.2s ease;
}

.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* 下拉菜单样式 */
.user-dropdown-menu {
  margin-top: 8px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.dropdown-item {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  font-size: 14px;
}

.dropdown-item:hover {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.logout-item:hover {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

/* 认证按钮 */
.auth-buttons {
  display: flex;
  gap: 8px;
}

.auth-btn {
  border-radius: 12px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s ease;
  border: none;
  font-size: 14px;
}

.login-btn {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.login-btn:hover {
  background: rgba(0, 0, 0, 0.08);
}

.register-btn {
  background: #007aff;
  color: white;
}

.register-btn:hover {
  background: #0056cc;
  transform: scale(1.02);
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mobile-menu-btn:hover {
  background: rgba(0, 0, 0, 0.08);
}

.mobile-menu-btn .el-icon {
  font-size: 18px;
}

/* 移动端抽屉菜单 */
.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: #fafafa;
  color: #1d1d1f;
}

.mobile-menu-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.mobile-logo-icon {
  font-size: 1.75rem;
  color: #007aff;
}

.mobile-logo-text {
  font-size: 1.125rem;
  font-weight: 600;
}

.mobile-nav {
  flex: 1;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 4px 0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
}

.mobile-nav-item:hover {
  background: rgba(0, 122, 255, 0.1);
}

.mobile-nav-item.active {
  background: rgba(0, 122, 255, 0.15);
  color: #007aff;
  font-weight: 600;
}

.mobile-nav-item .el-icon {
  font-size: 18px;
}

.mobile-user-section {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding-top: 20px;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.mobile-username {
  font-size: 16px;
  font-weight: 600;
}

.mobile-user-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mobile-user-actions .el-button {
  justify-content: flex-start;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
  border: none;
  color: #1d1d1f;
}

.mobile-auth-section {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-auth-btn {
  width: 100%;
  border-radius: 12px;
  padding: 12px;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    padding: 0 20px;
  }
  
  .nav-menu {
    margin: 0 20px;
  }
  
  .logo-text {
    font-size: 1.125rem;
  }
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .auth-buttons .auth-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .username {
    display: none;
  }
  
  .notification-btn {
    display: none;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 16px;
    height: 56px;
  }
  
  .logo-text {
    display: none;
  }
  
  .logo-icon {
    font-size: 1.5rem;
  }
  
  .auth-buttons {
    gap: 6px;
  }
  
  .auth-btn {
    padding: 6px 10px;
    font-size: 12px;
  }
}

/* 滚动时的样式变化 */
.header-container.scrolled {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 1px 20px rgba(0, 0, 0, 0.08);
}
</style>