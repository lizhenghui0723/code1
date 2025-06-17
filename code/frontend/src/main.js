import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'
import './assets/global.css'
import router from './router'

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.timeout = 5000

// 添加请求拦截器，自动为所有请求加上JWT token
axios.interceptors.request.use(config => {
  // 从localStorage获取token
  const token = localStorage.getItem('token')
  if (token) {
    // 在请求头加上Authorization: Bearer <token>
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
}, error => {
  return Promise.reject(error)
})

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')
