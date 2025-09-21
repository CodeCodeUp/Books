<template>
  <div class="book-list-container">
    <!-- 搜索栏区域 -->
    <div class="search-section" data-aos="fade-down">
      <div class="search-header">
        <h1 class="page-title">
          <el-icon class="title-icon"><Collection /></el-icon>
          图书宝库
        </h1>
        <p class="page-subtitle">探索{{ total.toLocaleString() }}本精选图书</p>
      </div>
      
      <div class="search-bar-container">
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索书名、作者、或关键词..."
            @keyup.enter="handleSearch"
            size="large"
            clearable
            class="search-input"
          >
            <template #prepend>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button 
                @click="handleSearch" 
                :loading="loading"
                type="primary"
                class="search-btn"
              >
                搜索
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>

    <!-- 筛选和排序栏 -->
    <div class="filter-section" data-aos="fade-up" data-aos-delay="100">
      <div class="filter-container">
        <div class="filter-left">
          <!-- 删除排序和年份筛选 -->
        </div>
        
        <div class="filter-right">
          <div class="view-mode-switch">
            <el-radio-group v-model="viewMode" @change="handleViewModeChange">
              <el-radio-button value="grid">
                <el-icon><Grid /></el-icon>
                网格
              </el-radio-button>
              <el-radio-button value="list">
                <el-icon><List /></el-icon>
                列表
              </el-radio-button>
            </el-radio-group>
          </div>
          
          <div class="results-info">
            <span class="results-count">共找到 {{ total.toLocaleString() }} 本图书</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图书展示区域 -->
    <div class="books-section">
      <div 
        :class="['book-grid', viewMode]" 
        v-loading="loading"
        element-loading-text="正在加载精彩图书..."
        element-loading-background="rgba(255, 255, 255, 0.9)"
      >
        <div 
          v-for="(book, index) in books" 
          :key="book.bookId"
          :data-aos="'zoom-in'"
          :data-aos-delay="Math.min(index * 50, 500)"
          class="book-item-wrapper"
        >
          <BookCard 
            :book="book" 
            :class="{ 'list-view': viewMode === 'list' }"
          />
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && books.length === 0" class="empty-state" data-aos="fade-up">
        <div class="empty-icon">📚</div>
        <h3>暂无图书</h3>
        <p>尝试调整搜索条件或浏览其他分类</p>
        <el-button type="primary" @click="clearSearch">
          <el-icon><Refresh /></el-icon>
          重新搜索
        </el-button>
      </div>
    </div>
    
    <!-- 分页器 -->
    <div class="pagination-section" v-if="total > 0" data-aos="fade-up">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 40, 60, 80]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="custom-pagination"
        background
      />
      
      <!-- 回到顶部按钮 -->
      <el-backtop 
        :right="100" 
        :bottom="100"
        :visibility-height="300"
        class="back-top-btn"
      >
        <div class="back-top-content">
          <el-icon><Top /></el-icon>
        </div>
      </el-backtop>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { bookApi } from '../api/book'
import BookCard from '../components/BookCard.vue'
import { ElMessage } from 'element-plus'
import { 
  Search, Collection, Grid, List, Refresh, Top 
} from '@element-plus/icons-vue'

const books = ref([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const viewMode = ref('grid')

// 快捷搜索标签已删除

const loadBooks = async () => {
  loading.value = true
  try {
    const response = await bookApi.getBooks(
      currentPage.value, 
      pageSize.value, 
      searchKeyword.value
    )
    books.value = response.data.records || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载图书失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadBooks()
}

const clearSearch = () => {
  searchKeyword.value = ''
  currentPage.value = 1
  loadBooks()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadBooks()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadBooks()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleViewModeChange = (mode) => {
  viewMode.value = mode
  // 触发重新渲染动画
  document.querySelectorAll('[data-aos]').forEach(el => {
    el.classList.remove('aos-animate')
    setTimeout(() => el.classList.add('aos-animate'), 50)
  })
}

// 监听搜索关键词变化，实现实时搜索
watch(searchKeyword, (newVal) => {
  if (!newVal) {
    handleSearch()
  }
})

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.book-list-container {
  min-height: 100vh;
  background: #fafafa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 搜索栏区域 - 苹果风格 */
.search-section {
  background: white;
  padding: 40px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.search-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #1d1d1f;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  letter-spacing: -0.02em;
}

.title-icon {
  font-size: 2.5rem;
  color: #007aff;
}

.page-subtitle {
  font-size: 1.3rem;
  color: #86868b;
  font-weight: 400;
  margin: 0;
}

.search-bar-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.search-bar {
  margin-bottom: 25px;
}

.search-input {
  border-radius: 50px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 50px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: none;
  padding: 0 20px;
  height: 60px;
  background: #f5f5f7;
}

.search-input :deep(.el-input-group__prepend) {
  background: #e5e5e7;
  border: none;
  border-radius: 50px 0 0 50px;
  padding: 0 15px;
  color: #86868b;
}

.search-btn {
  border-radius: 0 50px 50px 0;
  background: #007aff;
  border: none;
  padding: 0 25px;
  height: 60px;
  font-weight: 600;
  color: white;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: #0056cc;
  transform: scale(1.02);
}

/* 筛选区域 */
.filter-section {
  padding: 30px 20px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.filter-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}

.filter-left {
  /* 空的，已删除排序功能 */
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.view-mode-switch :deep(.el-radio-button) {
  border-radius: 20px;
}

.view-mode-switch :deep(.el-radio-button__inner) {
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #1d1d1f;
  background: #f5f5f7;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

.view-mode-switch :deep(.el-radio-button__original:checked + .el-radio-button__inner) {
  background: #007aff;
  border-color: #007aff;
  color: white;
}

.results-info {
  font-size: 14px;
  color: #86868b;
  font-weight: 500;
}

.results-count {
  background: rgba(0, 122, 255, 0.1);
  padding: 6px 12px;
  border-radius: 15px;
  color: #007aff;
}

/* 图书展示区域 */
.books-section {
  padding: 40px 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 60vh;
}

.book-grid {
  display: grid;
  gap: 30px;
  margin-bottom: 40px;
}

.book-grid.grid {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.book-grid.list {
  grid-template-columns: 1fr;
  gap: 20px;
}

.book-item-wrapper {
  transition: all 0.3s ease;
}

/* 列表视图样式 */
.book-grid.list .book-card {
  height: auto;
  padding: 20px;
}

.book-grid.list .book-image-container {
  float: left;
  margin-right: 20px;
  margin-bottom: 0;
  padding: 0;
}

.book-grid.list .book-info {
  overflow: hidden;
  text-align: left;
  padding: 0;
}

.book-grid.list .book-title {
  font-size: 18px;
  min-height: auto;
}

.book-grid.list .enhanced-info {
  margin-top: 20px;
}

.book-grid.list .action-buttons {
  justify-content: flex-start;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #718096;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin: 0 0 10px 0;
  color: #4a5568;
}

.empty-state p {
  font-size: 1rem;
  margin: 0 0 30px 0;
}

/* 分页区域 */
.pagination-section {
  background: white;
  padding: 40px 20px;
  text-align: center;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.custom-pagination {
  display: inline-flex;
  background: white;
  border-radius: 50px;
  padding: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.custom-pagination :deep(.el-pager li) {
  background: transparent;
  border-radius: 25px;
  margin: 0 2px;
  transition: all 0.3s ease;
}

.custom-pagination :deep(.el-pager li:hover),
.custom-pagination :deep(.el-pager li.is-active) {
  background: #007aff;
  color: white;
  transform: scale(1.1);
}

/* 回到顶部按钮 */
.back-top-btn :deep(.el-backtop) {
  background: #007aff;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 122, 255, 0.3);
}

.back-top-content {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .filter-container {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .filter-right {
    justify-content: space-between;
  }
  
  .book-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2.2rem;
    flex-direction: column;
    gap: 10px;
  }
  
  .search-input :deep(.el-input__wrapper) {
    height: 50px;
  }
  
  .search-btn {
    height: 50px;
    padding: 0 20px;
  }
  
  .filter-right {
    flex-direction: column;
    width: 100%;
  }
  
  .view-mode-switch {
    width: 100%;
  }
  
  .book-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .book-grid.list .book-image-container {
    float: none;
    margin-right: 0;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .book-grid.list .book-info {
    text-align: center;
  }
  
  .book-grid.list .action-buttons {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .book-grid.grid {
    grid-template-columns: 1fr;
  }
}

/* 加载动画优化 */
.books-section :deep(.el-loading-mask) {
  background: rgba(248, 250, 252, 0.9);
  backdrop-filter: blur(5px);
}

.books-section :deep(.el-loading-text) {
  color: #007aff;
  font-weight: 500;
}

.books-section :deep(.el-loading-spinner) {
  color: #007aff;
}
</style>