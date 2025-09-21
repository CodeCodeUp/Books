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
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-header {
  background-color: #545c64;
  color: white;
  padding: 0;
}

.el-main {
  padding: 20px;
}</style>