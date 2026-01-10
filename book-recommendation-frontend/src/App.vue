<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航 -->
      <el-header>
        <Header />
      </el-header>
      
      <!-- 主要内容区域 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import Header from './components/Header.vue'
</script>

<style>
/* Zen-iOS Hybrid 全局样式 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: #F2F2F7;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #F2F2F7;
  min-height: 100vh;
}

.el-header {
  background-color: rgba(84, 92, 100, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  color: white;
  padding: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.el-main {
  padding: 20px;
  background-color: #F2F2F7;
}

/* 全局卡片毛玻璃基础样式 */
.el-card {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.08);
  border-radius: 20px;
}

.el-card:hover {
  box-shadow: 0 8px 32px -1px rgba(0, 0, 0, 0.12);
}

/* 全局按钮触觉反馈 */
.el-button {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.el-button:active {
  transform: scale(0.97);
}
</style>