<template>
  <div class="stock-log-container">
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="商品名称">
          <el-input v-model="searchForm.product_name" placeholder="请输入商品名称" clearable @keyup.enter="handleSearch" style="width: 180px" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="入库" value="入库" />
            <el-option label="出库" value="出库" />
            <el-option label="调整" value="调整" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间区间">
          <el-date-picker v-model="searchForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon>搜索</el-button>
          <el-button @click="resetSearch"><el-icon><Refresh /></el-icon>重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card class="table-card" shadow="never">
      <div class="sort-bar">
        <span class="sort-label">排序：</span>
        <el-radio-group v-model="sortBy" size="small" @change="handleSort">
          <el-radio-button label="timestamp">时间</el-radio-button>
          <el-radio-button label="change">变动数量</el-radio-button>
        </el-radio-group>
        <el-radio-group v-model="sortOrder" size="small" @change="handleSort" style="margin-left: 20px">
          <el-radio-button label="desc"><el-icon><SortDown /></el-icon>降序</el-radio-button>
          <el-radio-button label="asc"><el-icon><SortUp /></el-icon>升序</el-radio-button>
        </el-radio-group>
      </div>
      <el-table :data="logs" style="width:100%" :border="true" size="large" v-loading="loading" @sort-change="handleTableSort">
        <el-table-column prop="product.name" label="商品名称" min-width="160">
          <template #default="{ row }">
            {{ row.product && row.product.name ? row.product.name : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="change" label="变动" width="100" sortable="custom" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="before_stock" label="变动前库存" width="120" />
        <el-table-column prop="after_stock" label="变动后库存" width="120" />
        <el-table-column prop="timestamp" label="时间" width="180" sortable="custom">
          <template #default="{ row }">{{ formatTime(row.timestamp) }}</template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Search, Refresh, SortDown, SortUp } from '@element-plus/icons-vue'
const logs = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const sortBy = ref('timestamp')
const sortOrder = ref('desc')
const searchForm = reactive({
  product_name: '',
  type: '',
  dateRange: []
})
async function fetchLogs() {
  loading.value = true
  let params = {
    page: currentPage.value,
    page_size: pageSize.value,
    sort_by: sortBy.value,
    sort_order: sortOrder.value
  }
  if (searchForm.product_name) params.product_name = searchForm.product_name
  if (searchForm.type) params.type = searchForm.type
  if (searchForm.dateRange && searchForm.dateRange.length === 2) {
    params.start_time = searchForm.dateRange[0]
    params.end_time = searchForm.dateRange[1]
  }
  try {
    const res = await axios.get('/api/stock_logs', { params })
    logs.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取库存流水失败')
  } finally {
    loading.value = false
  }
}
function handleSearch() {
  currentPage.value = 1
  fetchLogs()
}
function resetSearch() {
  searchForm.product_name = ''
  searchForm.type = ''
  searchForm.dateRange = []
  handleSearch()
}
function handleSort() {
  currentPage.value = 1
  fetchLogs()
}
function handleTableSort(event) {
  if (event.column) {
    sortBy.value = event.column.property
    sortOrder.value = event.order === 'ascending' ? 'asc' : 'desc'
    currentPage.value = 1
    fetchLogs()
  }
}
function handleSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
  fetchLogs()
}
function handlePageChange(newPage) {
  currentPage.value = newPage
  fetchLogs()
}
function formatTime(time) {
  return new Date(time).toLocaleString('zh-CN')
}
onMounted(fetchLogs)
</script>
<style scoped>
.stock-log-container {
  padding: 0;
}
.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
}
.search-form {
  margin-bottom: 20px;
}
.table-card {
  border-radius: 8px;
}
.sort-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
.sort-label {
  font-weight: 500;
  margin-right: 10px;
  color: #606266;
}
</style> 