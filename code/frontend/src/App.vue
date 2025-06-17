<template>
  <el-container class="root-container">
    <el-header height="60px" class="header">
      <div class="logo">
        <el-icon :size="24" style="margin-right: 8px"><DataAnalysis /></el-icon>
        ERP智能管理系统
      </div>
      <div class="header-right">
        <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
          <el-button type="text" @click="showNotifications = true">
            <el-icon :size="20"><Bell /></el-icon>
          </el-button>
        </el-badge>
        <el-dropdown v-if="user" @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ user.username }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="aside" v-if="user">
        <el-menu :default-active="activeMenu" @select="handleMenu" class="menu">
          <el-menu-item index="dashboard">
            <el-icon><DataLine /></el-icon>
            <span>数据大屏</span>
          </el-menu-item>
          <el-sub-menu index="products">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>商品管理</span>
            </template>
            <el-menu-item index="product-list">商品列表</el-menu-item>
            <el-menu-item index="category">商品分类</el-menu-item>
            <el-menu-item index="import-export">导入导出</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="sales">
            <template #title>
              <el-icon><ShoppingCart /></el-icon>
              <span>销售管理</span>
            </template>
            <el-menu-item index="sales-order">销售订单</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="stock">
            <el-icon><Box /></el-icon>
            <span>库存流水</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <login-view v-if="!user" @login-success="onLoginSuccess" />
        <dashboard-view v-else-if="activeMenu==='dashboard'" />
        <product-list-view v-else-if="activeMenu==='product-list'" />
        <category-view v-else-if="activeMenu==='category'" />
        <import-export-view v-else-if="activeMenu==='import-export'" />
        <sales-order-view v-else-if="activeMenu==='sales-order'" />
        <stock-log-view v-else-if="activeMenu==='stock'" />
      </el-main>
    </el-container>
    
    <!-- 通知抽屉 -->
    <el-drawer
      v-model="showNotifications"
      title="系统通知"
      :size="400"
      direction="rtl"
    >
      <notification-list @update="fetchUnreadCount" />
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { 
  DataAnalysis, 
  Bell, 
  User, 
  ArrowDown, 
  DataLine, 
  Goods, 
  ShoppingCart, 
  Box 
} from '@element-plus/icons-vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import ProductListView from './views/ProductListView.vue'
import CategoryView from './views/CategoryView.vue'
import ImportExportView from './views/ImportExportView.vue'
import SalesOrderView from './views/SalesOrderView.vue'
import StockLogView from './views/StockLogView.vue'
import NotificationList from './components/NotificationList.vue'

const user = ref(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null)
const activeMenu = ref('dashboard')
const showNotifications = ref(false)
const unreadCount = ref(0)

// 获取未读通知数量
async function fetchUnreadCount() {
  if (!user.value) return
  try {
    const res = await axios.get('/api/notifications?is_read=false')
    unreadCount.value = res.data.length
  } catch (error) {
    console.error('获取通知失败:', error)
  }
}

function onLoginSuccess(u) {
  user.value = u
  localStorage.setItem('user', JSON.stringify(u))
  fetchUnreadCount()
}

function handleCommand(command) {
  if (command === 'logout') {
    user.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    activeMenu.value = 'dashboard'
    ElMessage.success('已退出登录')
  }
}

function handleMenu(index) {
  activeMenu.value = index
}

onMounted(() => {
  if (user.value) {
    fetchUnreadCount()
    // 定时刷新未读通知数
    setInterval(fetchUnreadCount, 30000)
  }
})

document.title = 'ERP智能管理系统'
</script>

<style scoped>
.root-container {
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  height: 60px !important;
}
.logo {
  font-size: 20px;
  font-weight: bold;
  display: flex;
  align-items: center;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.notification-badge {
  margin-right: 10px;
}
.notification-badge :deep(.el-button) {
  color: white;
}
.user-info {
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
.el-container {
  margin-top: 60px;
}
.aside {
  background: #fff;
  border-right: 1px solid #f0f0f0;
  min-height: calc(100vh - 60px);
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  z-index: 1000;
  width: 200px !important;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0,0,0,0.05);
}
.menu {
  border: none;
}
.main-content {
  margin-left: 200px;
  padding: 24px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}
@media (max-width: 768px) {
  .aside {
    width: 100px !important;
  }
  .main-content {
    margin-left: 100px;
  }
  .logo {
    font-size: 16px;
  }
}

/* 美化滚动条 */
.aside::-webkit-scrollbar {
  width: 6px;
}
.aside::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.aside::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}
.aside::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
