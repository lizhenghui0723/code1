<template>
  <div>
    <el-row justify="space-between" align="middle" style="margin-bottom:16px;">
      <el-col><h2>库存流水</h2></el-col>
      <el-col>
        <el-input v-model="pid" placeholder="按商品ID筛选" style="width:180px;" clearable @change="fetchLogs" />
      </el-col>
    </el-row>
    <el-table :data="logs" style="width:100%" :border="true" size="large" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60"/>
      <el-table-column prop="product_id" label="商品ID"/>
      <el-table-column prop="change" label="变动"/>
      <el-table-column prop="type" label="类型"/>
      <el-table-column prop="timestamp" label="时间"/>
    </el-table>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const logs = ref([])
const loading = ref(false)
const pid = ref('')
async function fetchLogs() {
  loading.value = true
  let url = '/api/stock_logs'
  if (pid.value) url += `?product_id=${pid.value}`
  const res = await axios.get(url)
  logs.value = res.data
  loading.value = false
}
onMounted(fetchLogs)
</script>
<style scoped>
h2 { margin: 0 0 12px 0; }
@media (max-width: 600px) {
  .el-table { font-size: 12px; }
}
</style> 