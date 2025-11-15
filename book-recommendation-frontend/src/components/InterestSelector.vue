<template>
  <div class="interest-selector-container">
    <!-- 顶部标题 - 简约蓝白风格 -->
    <div class="header-section">
      <h1 class="main-title">{{ title || '选择您的兴趣' }}</h1>
      <p class="subtitle">已选择 <span class="count-highlight">{{ selectedIds.length }}</span> 个</p>
    </div>

    <!-- 圆形气泡区域 - Apple风格 -->
    <div class="circular-wrapper">
      <div class="circular-container">
        <div
          v-for="(theme, index) in currentPageCategories"
          :key="theme.themeId"
          :class="['floating-bubble', { 'selected': isSelected(theme.themeId) }]"
          :style="getCircularBubbleStyle(index)"
          @click="toggleSelection(theme.themeId)"
        >
          <div class="bubble-content">
            <div class="emoji-icon">{{ getThemeEmoji(theme.themeNameEn) }}</div>
            <div class="theme-name">{{ theme.themeNameZh }}</div>
          </div>
          <div class="bubble-glow"></div>
        </div>
      </div>

      <!-- 分页指示器 -->
      <div class="page-indicator-wrapper" v-if="totalPages > 1">
        <button
          @click="prevPage"
          :disabled="currentPage === 0"
          class="page-nav-btn"
          type="button"
        >
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <span class="page-text">{{ currentPage + 1 }} / {{ totalPages }}</span>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages - 1"
          class="page-nav-btn"
          type="button"
        >
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
    </div>

    <!-- 底部操作区 - 极简设计 -->
    <div class="action-section">
      <div class="action-row">
        <button @click="selectRandom" class="secondary-btn" type="button">
          <el-icon><Refresh /></el-icon>
          <span>随机选择</span>
        </button>
        <button @click="selectAll" class="secondary-btn" type="button">
          <el-icon><Check /></el-icon>
          <span>{{ allSelected ? '清空' : '全选' }}</span>
        </button>
      </div>

      <button
        @click="handleConfirm"
        :disabled="!canConfirm && minSelection > 0"
        class="primary-btn"
        type="button"
      >
        {{ confirmText || '保存兴趣' }}
      </button>

      <button
        v-if="allowSkip"
        @click="handleSkip"
        class="skip-btn"
        type="button"
      >
        {{ skipText || '跳过' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { categoryApi } from '../api/category'
import { ElMessage } from 'element-plus'
import { Refresh, Check, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: '兴趣选择'
  },
  subtitle: {
    type: String,
    default: ''
  },
  minSelection: {
    type: Number,
    default: 0
  },
  randomCount: {
    type: Number,
    default: 5
  },
  confirmText: {
    type: String,
    default: '保存兴趣'
  },
  skipText: {
    type: String,
    default: '暂时跳过'
  },
  allowSkip: {
    type: Boolean,
    default: true
  },
  initialSelected: {
    type: Array,
    default: () => []
  },
  pageSize: {
    type: Number,
    default: 8
  }
})

const emit = defineEmits(['confirm', 'skip'])

const loading = ref(false)
const categories = ref([])
const selectedIds = ref([...props.initialSelected])
const currentPage = ref(0)

// 分页
const totalPages = computed(() => Math.ceil(categories.value.length / props.pageSize))
const currentPageCategories = computed(() => {
  const start = currentPage.value * props.pageSize
  return categories.value.slice(start, start + props.pageSize)
})

const nextPage = () => {
  if (currentPage.value < totalPages.value - 1) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
  }
}

// Emoji映射表
const themeEmojis = {
  'Literature': '📚',
  'Science Fiction': '🚀',
  'Fantasy': '🐉',
  'Mystery': '🔍',
  'Romance': '💕',
  'History': '⏳',
  'Biography': '👤',
  'Self-Help': '💪',
  'Business': '💼',
  'Science': '🔬',
  'Psychology': '🧠',
  'Philosophy': '🤔',
  'Poetry': '✍️',
  'Art': '🎨',
  'Travel': '✈️',
  'Cooking': '🍳',
  'Health': '🏥',
  'Religion': '📿',
  'Sports': '⚽',
  'Music': '🎵',
  'Comics': '📰',
  'Horror': '👻',
  'True Crime': '🔪',
  'Education': '🎓',
  'Technology': '💻',
  'Politics': '🏛️',
  'Humor': '😄',
  'Drama': '🎭',
  "Children's": '🧸',
  'Young Adult': '🎒',
  'Classics': '📖'
}

const getThemeEmoji = (themeName) => {
  return themeEmojis[themeName] || '📕'
}

// 智能网格布局 - 绝对不重叠
const getCircularBubbleStyle = (index) => {
  const total = currentPageCategories.value.length

  if (total === 1) {
    return {
      left: '50%',
      top: '50%',
      width: '120px',
      height: '120px',
      animationDelay: '0s'
    }
  }

  // 使用种子确保同一页每次刷新位置相同
  const seed = currentPage.value * 1000 + index
  const random = (s) => {
    const x = Math.sin(s) * 10000
    return x - Math.floor(x)
  }

  // 根据气泡数量选择最优网格布局
  let gridPositions = []

  if (total <= 4) {
    // 2x2 网格
    gridPositions = [
      { x: 30, y: 30 }, { x: 70, y: 30 },
      { x: 30, y: 70 }, { x: 70, y: 70 }
    ]
  } else if (total <= 6) {
    // 3x2 网格（更宽松）
    gridPositions = [
      { x: 25, y: 30 }, { x: 50, y: 30 }, { x: 75, y: 30 },
      { x: 25, y: 70 }, { x: 50, y: 70 }, { x: 75, y: 70 }
    ]
  } else {
    // 3x3 网格 - 间距更大
    gridPositions = [
      { x: 20, y: 22 }, { x: 50, y: 22 }, { x: 80, y: 22 },
      { x: 20, y: 50 }, { x: 50, y: 50 }, { x: 80, y: 50 },
      { x: 20, y: 78 }, { x: 50, y: 78 }, { x: 80, y: 78 }
    ]
  }

  // 获取基础网格位置
  const basePos = gridPositions[index % gridPositions.length]

  // 添加极轻微的随机偏移（±3%），营造自然感但避免重叠
  const offsetX = (random(seed + 5) - 0.5) * 6  // ±3%
  const offsetY = (random(seed + 6) - 0.5) * 6

  const x = basePos.x + offsetX
  const y = basePos.y + offsetY

  // 气泡大小：108-118px（范围更小，更统一）
  const sizeRandom = random(seed + 1)
  let size
  if (sizeRandom < 0.35) {
    size = 108 + Math.floor(random(seed + 2) * 4)   // 35% 小球 108-112px
  } else if (sizeRandom < 0.7) {
    size = 112 + Math.floor(random(seed + 3) * 4)   // 35% 中球 112-116px
  } else {
    size = 116 + Math.floor(random(seed + 4) * 2)   // 30% 大球 116-118px
  }

  // 随机动画延迟
  const delay = random(seed + 7) * 0.6

  // 浮动动画参数 - 减小浮动距离避免碰撞
  const floatDuration = 3.5 + random(seed + 8) * 2.5
  const floatDelay = random(seed + 9) * 2
  const floatDistance = 4 + random(seed + 10) * 5  // 4-9px（减小浮动范围）

  return {
    left: `${x}%`,
    top: `${y}%`,
    width: `${size}px`,
    height: `${size}px`,
    animationDelay: `${delay}s`,
    '--float-duration': `${floatDuration}s`,
    '--float-delay': `${floatDelay}s`,
    '--float-distance': `${floatDistance}px`
  }
}

const isSelected = (themeId) => {
  return selectedIds.value.includes(themeId)
}

const toggleSelection = (themeId) => {
  const index = selectedIds.value.indexOf(themeId)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(themeId)
  }
}

const allSelected = computed(() => {
  return categories.value.length > 0 && selectedIds.value.length === categories.value.length
})

const canConfirm = computed(() => {
  return selectedIds.value.length >= props.minSelection
})

const selectAll = () => {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = categories.value.map(c => c.themeId)
  }
}

const selectRandom = () => {
  selectedIds.value = []
  const shuffled = [...categories.value].sort(() => 0.5 - Math.random())
  const randomSelected = shuffled.slice(0, Math.min(props.randomCount, categories.value.length))
  selectedIds.value = randomSelected.map(c => c.themeId)
  ElMessage.success(`已随机选择 ${selectedIds.value.length} 个兴趣`)
}

const handleConfirm = () => {
  if (!canConfirm.value && props.minSelection > 0) {
    ElMessage.warning(`请至少选择 ${props.minSelection} 个兴趣`)
    return
  }
  emit('confirm', selectedIds.value)
}

const handleSkip = () => {
  if (!props.allowSkip) return
  emit('skip')
}

const loadCategories = async () => {
  loading.value = true
  try {
    const response = await categoryApi.getAllCategories()
    categories.value = response.data || []
  } catch (error) {
    ElMessage.error('加载失败')
    categories.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
/* Apple风格 - 蓝白简约设计 */
.interest-selector-container {
  width: 100%;
  max-width: 920px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 20px;
  box-shadow:
    0 8px 30px rgba(0, 0, 0, 0.08),
    0 2px 10px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', sans-serif;
}

/* 顶部标题区 - 极简设计 */
.header-section {
  text-align: center;
  padding: 36px 32px 24px;
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.main-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  letter-spacing: -0.03em;
}

.subtitle {
  font-size: 0.9375rem;
  color: #6e6e73;
  margin: 0;
  font-weight: 400;
}

.count-highlight {
  display: inline-block;
  min-width: 24px;
  padding: 2px 10px;
  background: linear-gradient(135deg, #5ac8fa 0%, #42a5f5 100%);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.875rem;
  border-radius: 12px;
  margin: 0 4px;
  box-shadow: 0 2px 8px rgba(90, 200, 250, 0.3);
}

/* 圆形气泡容器 */
.circular-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 32px 36px;
  background: #fafafa;
  gap: 32px;
}

.circular-container {
  position: relative;
  width: 100%;
  max-width: 700px;
  height: 500px;
  margin: 0 auto;
}

/* 超强3D悬浮气泡 - 自然散落风格 */
.floating-bubble {
  position: absolute;
  border-radius: 50%;
  background:
    linear-gradient(145deg, #ffffff 0%, #f5f7fa 100%);
  cursor: pointer;
  transition: all 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform: translate(-50%, -50%);
  user-select: none;
  z-index: 1;

  /* 超强3D立体阴影 */
  box-shadow:
    0 12px 28px rgba(0, 0, 0, 0.12),
    0 6px 12px rgba(0, 0, 0, 0.08),
    0 2px 4px rgba(0, 0, 0, 0.04),
    inset 0 -4px 8px rgba(0, 0, 0, 0.05),
    inset 0 3px 8px rgba(255, 255, 255, 0.9);

  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);

  /* 入场动画 + 持续浮动动画 */
  animation:
    floatIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) both,
    gentleFloat var(--float-duration, 4s) ease-in-out var(--float-delay, 0s) infinite;
}

.floating-bubble:hover {
  /* hover时提升到最上层 */
  z-index: 10;
  /* hover时暂停浮动动画，只保留缩放效果 */
  animation-play-state: paused, paused;
  transform: translate(-50%, -50%) scale(1.12) translateY(-8px);
  box-shadow:
    0 20px 45px rgba(0, 0, 0, 0.15),
    0 10px 20px rgba(0, 0, 0, 0.1),
    0 4px 8px rgba(0, 0, 0, 0.06),
    inset 0 -5px 10px rgba(0, 0, 0, 0.06),
    inset 0 4px 12px rgba(255, 255, 255, 1);
}

/* 选中状态 - 浅蓝色渐变发光 */
.floating-bubble.selected {
  background: linear-gradient(145deg, #8ac9ff 0%, #5ac8fa 50%, #42a5f5 100%);
  border: 1px solid rgba(255, 255, 255, 0.7);
  z-index: 5;

  box-shadow:
    0 18px 50px rgba(90, 200, 250, 0.45),
    0 10px 25px rgba(90, 200, 250, 0.3),
    0 5px 12px rgba(66, 165, 245, 0.25),
    inset 0 -6px 12px rgba(66, 165, 245, 0.25),
    inset 0 4px 12px rgba(255, 255, 255, 0.7);

  /* 选中状态继续保持浮动动画 */
  animation:
    floatIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) both,
    gentleFloat var(--float-duration, 4s) ease-in-out var(--float-delay, 0s) infinite;
}

.floating-bubble.selected:hover {
  z-index: 15;
  animation-play-state: paused, paused;
  transform: translate(-50%, -50%) scale(1.24) translateY(-12px);
  box-shadow:
    0 24px 60px rgba(90, 200, 250, 0.5),
    0 14px 32px rgba(90, 200, 250, 0.35),
    0 6px 16px rgba(66, 165, 245, 0.3),
    inset 0 -6px 14px rgba(66, 165, 245, 0.3),
    inset 0 5px 14px rgba(255, 255, 255, 0.8);
}

/* 气泡发光层 */
.bubble-glow {
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  opacity: 0;
  background: radial-gradient(circle, rgba(90, 200, 250, 0.35) 0%, transparent 70%);
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.floating-bubble.selected .bubble-glow {
  opacity: 1;
  animation: pulse 2s ease-in-out infinite;
}

.bubble-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
}

.emoji-icon {
  font-size: 2.75rem;
  line-height: 1;
  opacity: 0.75;
  transition: all 0.35s ease;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.12));
}

.floating-bubble.selected .emoji-icon {
  opacity: 1;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.25));
  transform: scale(1.1);
}

.theme-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1d1d1f;
  text-align: center;
  line-height: 1.3;
  transition: all 0.35s ease;
  letter-spacing: -0.01em;
}

.floating-bubble.selected .theme-name {
  color: #ffffff;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transform: scale(1.05);
}

/* 分页指示器 - Apple风格 */
.page-indicator-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 28px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.08),
    0 2px 4px rgba(0, 0, 0, 0.04);
}

.page-nav-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #5ac8fa;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.page-nav-btn:hover:not(:disabled) {
  background: rgba(90, 200, 250, 0.15);
  transform: scale(1.1);
}

.page-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-text {
  font-size: 0.9375rem;
  color: #1d1d1f;
  font-weight: 600;
  min-width: 60px;
  text-align: center;
  letter-spacing: -0.02em;
}

/* 底部操作区 - 极简设计 */
.action-section {
  background: #ffffff;
  padding: 24px 32px 28px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-row {
  display: flex;
  gap: 12px;
}

.secondary-btn {
  flex: 1;
  height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #f5f5f7;
  color: #1d1d1f;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.secondary-btn:hover {
  background: #e8e8ed;
  border-color: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.primary-btn {
  width: 100%;
  height: 52px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #5ac8fa 0%, #42a5f5 100%);
  color: #ffffff;
  font-size: 1.0625rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow:
    0 6px 16px rgba(90, 200, 250, 0.35),
    0 2px 6px rgba(66, 165, 245, 0.25);
  letter-spacing: -0.01em;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow:
    0 10px 24px rgba(90, 200, 250, 0.45),
    0 4px 10px rgba(66, 165, 245, 0.35);
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.skip-btn {
  width: 100%;
  height: 40px;
  border: none;
  background: transparent;
  color: #86868b;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.skip-btn:hover {
  color: #1d1d1f;
}

/* 动画 */
@keyframes floatIn {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5) translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1) translateY(0);
  }
}

/* 轻柔的持续浮动动画 */
@keyframes gentleFloat {
  0%, 100% {
    transform: translate(-50%, -50%) translateY(0) translateX(0);
  }
  25% {
    transform: translate(-50%, -50%) translateY(calc(var(--float-distance) * -0.6)) translateX(calc(var(--float-distance) * 0.4));
  }
  50% {
    transform: translate(-50%, -50%) translateY(calc(var(--float-distance) * -1.2)) translateX(0);
  }
  75% {
    transform: translate(-50%, -50%) translateY(calc(var(--float-distance) * -0.6)) translateX(calc(var(--float-distance) * -0.4));
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .interest-selector-container {
    border-radius: 0;
  }

  .header-section {
    padding: 28px 24px 20px;
  }

  .main-title {
    font-size: 1.5rem;
  }

  .circular-container {
    height: 380px;
    max-width: 400px;
  }

  .emoji-icon {
    font-size: 2rem;
  }

  .theme-name {
    font-size: 0.8125rem;
  }
}
</style>
