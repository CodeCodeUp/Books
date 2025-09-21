<template>
  <div class="recommendations">
    <h1>个性化推荐</h1>
    <p>基于您的阅读历史为您推荐感兴趣的图书</p>
    
    <div class="recommend-section">
      <el-alert
        title="推荐功能开发中"
        type="info"
        description="推荐算法正在开发中，敬请期待！"
        show-icon
        :closable="false"
      />
    </div>
  </div>
</template>

<script setup>
// 推荐功能预留，后续实现推荐算法后再完善
</script>

<style scoped>
.recommendations {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.recommend-section {
  margin-top: 40px;
}
</style>