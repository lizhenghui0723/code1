<template>
  <div class="notification-container">
    <!-- 操作栏 -->
    <div class="notification-header">
      <el-radio-group v-model="filterType" size="small" @change="fetchNotifications">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="unread">未读</el-radio-button>
      </el-radio-group>
      <el-button 
        type="primary" 
        size="small" 
        plain 
        @click="markAllRead"
        :disabled="!notifications.some(n => !n.is_read)"
      >
        全部标为已读
      </el-button>
    </div>

    <!-- 通知列表 -->
    <div class="notification-list">
      <el-empty v-if="!notifications.length" description="暂无通知" />
      <transition-group name="notification-fade">
        <div 
          v-for="notification in notifications" 
          :key="notification.id" 
          class="notification-item"
          :class="{ 'is-read': notification.is_read }"
        >
          <div class="notification-icon">
            <el-icon v-if="notification.type === 'warning'" class="warning-icon">
              <Warning />
            </el-icon>
            <el-icon v-else-if="notification.type === 'info'" class="info-icon">
              <InfoFilled />
            </el-icon>
            <el-icon v-else-if="notification.type === 'error'" class="error-icon">
              <CircleCloseFilled />
            </el-icon>
            <div v-if="!notification.is_read" class="unread-dot"></div>
          </div>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-text">{{ notification.content }}</div>
            <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
          </div>
          <div class="notification-actions">
            <el-button 
              v-if="!notification.is_read" 
              type="primary" 
              link 
              @click="markAsRead(notification.id)"
            >
              标为已读
            </el-button>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="notification-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { 
  Warning, 
  InfoFilled, 
  CircleCloseFilled,
  Loading
} from '@element-plus/icons-vue'

// 状态变量
const notifications = ref([])
const loading = ref(false)
const filterType = ref('all')

// 定义事件
const emit = defineEmits(['update'])

// 格式化时间
function formatTime(time) {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取通知列表
async function fetchNotifications() {
  loading.value = true
  try {
    const params = {}
    if (filterType.value === 'unread') {
      params.is_read = false
    }
    
    const res = await axios.get('/api/notifications', { params })
    notifications.value = res.data
  } catch (error) {
    console.error('获取通知失败:', error)
    ElMessage.error('获取通知失败')
  } finally {
    loading.value = false
  }
}

// 标记已读
async function markAsRead(id) {
  try {
    await axios.put(`/api/notifications/${id}/read`)
    
    // 更新本地状态
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
    }
    
    // 通知父组件更新未读数量
    emit('update')
    
    ElMessage.success('已标记为已读')
  } catch (error) {
    console.error('标记已读失败:', error)
    ElMessage.error('操作失败')
  }
}

// 全部标记已读
async function markAllRead() {
  try {
    await axios.put('/api/notifications/read-all')
    
    // 更新本地状态
    notifications.value.forEach(n => {
      n.is_read = true
    })
    
    // 通知父组件更新未读数量
    emit('update')
    
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    console.error('全部标记已读失败:', error)
    ElMessage.error('操作失败')
  }
}

// 初始化
onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.notification-header {
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.notification-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  position: relative;
  transition: background-color 0.3s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.is-read {
  opacity: 0.7;
}

.notification-icon {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.notification-icon .warning-icon {
  color: #e6a23c;
  font-size: 20px;
}

.notification-icon .info-icon {
  color: #409eff;
  font-size: 20px;
}

.notification-icon .error-icon {
  color: #f56c6c;
  font-size: 20px;
}

.unread-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #f56c6c;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 5px;
  color: #303133;
}

.notification-text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
  line-height: 1.5;
}

.notification-time {
  color: #909399;
  font-size: 12px;
}

.notification-actions {
  display: flex;
  align-items: center;
}

.notification-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #909399;
}

.notification-loading .el-icon {
  margin-right: 5px;
}

/* 过渡动画 */
.notification-fade-enter-active,
.notification-fade-leave-active {
  transition: all 0.3s ease;
}

.notification-fade-enter-from,
.notification-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 美化滚动条 */
.notification-list::-webkit-scrollbar {
  width: 6px;
}

.notification-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>

