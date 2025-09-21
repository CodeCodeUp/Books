<template>
  <el-card class="book-card" @click="goToDetail" shadow="hover">
    <div class="book-image">
      <img 
        :src="book.imageUrlM || '/default-book.jpg'" 
        :alt="book.title"
        @error="handleImageError"
      />
    </div>
    
    <div class="book-info">
      <h3 class="book-title">{{ book.title }}</h3>
      <p class="book-author">{{ book.author || '未知作者' }}</p>
      <div class="book-stats">
        <el-rate 
          v-model="displayRating" 
          disabled 
          show-score 
          :score-template="`${book.avgRating || 0}`"
        />
        <span class="rating-count">({{ book.ratingCount || 0 }}人评价)</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const displayRating = computed(() => {
  return props.book.avgRating || 0
})

const goToDetail = () => {
  router.push(`/books/${props.book.bookId}`)
}

const handleImageError = (event) => {
  event.target.src = '/default-book.jpg'
}
</script>

<style scoped>
.book-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.book-card:hover {
  transform: translateY(-2px);
}

.book-image {
  text-align: center;
  margin-bottom: 10px;
}

.book-image img {
  width: 120px;
  height: 160px;
  object-fit: cover;
  border-radius: 4px;
}

.book-info {
  text-align: center;
}

.book-title {
  font-size: 14px;
  font-weight: bold;
  margin: 10px 0 5px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 40px;
}

.book-author {
  font-size: 12px;
  color: #666;
  margin: 5px 0;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-stats {
  margin-top: 10px;
}

.rating-count {
  font-size: 12px;
  color: #999;
  margin-left: 5px;
}
</style>