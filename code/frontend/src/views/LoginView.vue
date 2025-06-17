<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-title">用户登录</div>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" placeholder="密码" show-password clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" @click="onLogin" :loading="loading">登录</el-button>
        </el-form-item>
        <el-form-item>
          <el-link type="primary" @click="showRegister=true">没有账号？注册</el-link>
        </el-form-item>
      </el-form>
    </el-card>
    <el-dialog v-model="showRegister" title="用户注册" width="350px">
      <el-form :model="regForm" :rules="rules" ref="regFormRef" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="regForm.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="regForm.password" placeholder="密码" show-password clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister=false">取消</el-button>
        <el-button type="primary" @click="onRegister" :loading="regLoading">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import CryptoJS from 'crypto-js'
const form = ref({ username: '', password: '' })
const regForm = ref({ username: '', password: '' })
const loading = ref(false)
const regLoading = ref(false)
const showRegister = ref(false)
const formRef = ref()
const regFormRef = ref()
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}
const emit = defineEmits(['login-success'])
async function onLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const md5Password = CryptoJS.MD5(form.value.password).toString()
    const params = new URLSearchParams()
    params.append('username', form.value.username)
    params.append('password', md5Password)
    const res = await axios.post('/api/token', params)
    localStorage.setItem('token', res.data.access_token)
    ElMessage.success('登录成功')
    emit('login-success', form.value.username)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
async function onRegister() {
  await regFormRef.value.validate()
  regLoading.value = true
  try {
    const md5Password = CryptoJS.MD5(regForm.value.password).toString()
    await axios.post('/api/register', {
      username: regForm.value.username,
      password: md5Password
    })
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    regLoading.value = false
  }
}
</script>
<style scoped>
.login-container {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f7fa;
}
.login-card {
  width: 350px;
  border-radius: 12px;
  box-shadow: 0 2px 16px #e0e0e0;
}
.login-title {
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 18px;
  color: #409eff;
}
@media (max-width: 500px) {
  .login-card { width: 95vw; }
}
</style> 