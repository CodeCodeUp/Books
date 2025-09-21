<template>
  <div class="book-list">
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索图书标题或作者"
        @keyup.enter="handleSearch"
        size="large"
        clearable
      >
        <template #append>
          <el-button @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
    
    <div class="book-grid" v-loading="loading">
      <BookCard 
        v-for="book in books" 
        :key="book.bookId" 
        :book="book" 
      />
    </div>
    
    <div class="pagination" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 40, 60, 80]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <el-empty v-if="!loading && books.length === 0" description="暂无图书数据" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bookApi } from '../api/book'
import BookCard from '../components/BookCard.vue'
import { ElMessage } from 'element-plus'

const books = ref([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)

const loadBooks = async () => {
  loading.value = true
  try {
    const response = await bookApi.getBooks(currentPage.value, pageSize.value, searchKeyword.value)
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

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadBooks()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadBooks()
}

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.book-list {
  max-width: 1200px;
  margin: 0 auto;
}

.search-bar {
  margin-bottom: 30px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>