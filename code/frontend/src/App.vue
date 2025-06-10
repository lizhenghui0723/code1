<template>
  <el-container class="root-container">
    <el-header height="60px" class="header">
      <div class="logo">ERP系统</div>
      <div class="header-right">
        <el-button v-if="user" type="text" @click="logout">退出登录</el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="aside" v-if="user">
        <el-menu :default-active="activeMenu" @select="handleMenu">
          <el-menu-item index="dashboard">商品管理</el-menu-item>
          <el-menu-item index="stock">库存流水</el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main-content">
        <login-view v-if="!user" @login-success="onLoginSuccess" />
        <dashboard-view v-else-if="activeMenu==='dashboard'" />
        <stock-log-view v-else-if="activeMenu==='stock'" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import StockLogView from './views/StockLogView.vue'

const user = ref(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null)
const activeMenu = ref('dashboard')

function onLoginSuccess(u) {
  user.value = u
  localStorage.setItem('user', JSON.stringify(u))
}
function logout() {
  user.value = null
  localStorage.removeItem('user')
  activeMenu.value = 'dashboard'
}
function handleMenu(index) {
  activeMenu.value = index
}

document.title = 'ERP系统'
</script>

<style scoped>
.root-container {
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 2px 8px #f0f1f2;
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
  color: #409eff;
}
.header-right {
  display: flex;
  align-items: center;
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
}
.main-content {
  margin-left: 200px;
  padding: 24px 12px 24px 12px;
  min-height: calc(100vh - 60px);
  background: #f7f7fa;
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
</style>
