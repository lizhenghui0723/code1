<template>
  <div class="import-export-container">
    <el-row :gutter="20">
      <!-- 数据导入 -->
      <el-col :xs="24" :md="12">
        <el-card class="import-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Upload /></el-icon>
                数据导入
              </span>
            </div>
          </template>
          
          <div class="import-section">
            <!-- 下载模板 -->
            <div class="template-section">
              <h4>第一步：下载导入模板</h4>
              <p class="tips">请先下载Excel模板，按照模板格式填写数据后再上传</p>
              <el-button type="primary" @click="downloadTemplate">
                <el-icon><Download /></el-icon>
                下载导入模板
              </el-button>
            </div>
            
            <!-- 上传文件 -->
            <div class="upload-section">
              <h4>第二步：上传Excel文件</h4>
              <el-upload
                ref="uploadRef"
                class="upload-demo"
                drag
                :action="uploadUrl"
                :headers="uploadHeaders"
                :before-upload="beforeUpload"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :show-file-list="false"
                accept=".xlsx,.xls"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    只能上传 Excel 文件，且不超过 10MB
                  </div>
                </template>
              </el-upload>
            </div>
            
            <!-- 导入结果 -->
            <div v-if="importResult" class="result-section">
              <h4>导入结果</h4>
              <el-alert
                :title="importResult.success_count > 0 ? '导入成功' : '导入失败'"
                :type="importResult.success_count > 0 ? 'success' : 'error'"
                :closable="false"
                show-icon
              >
                <p>成功导入：{{ importResult.success_count }} 条</p>
                <p v-if="importResult.error_count > 0">失败：{{ importResult.error_count }} 条</p>
              </el-alert>
              
              <div v-if="importResult.errors.length > 0" class="error-list">
                <h5>错误详情：</h5>
                <el-scrollbar max-height="200px">
                  <div v-for="(error, index) in importResult.errors" :key="index" class="error-item">
                    <el-icon color="#F56C6C"><CircleClose /></el-icon>
                    {{ error }}
                  </div>
                </el-scrollbar>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 数据导出 -->
      <el-col :xs="24" :md="12">
        <el-card class="export-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Download /></el-icon>
                数据导出
              </span>
            </div>
          </template>
          
          <div class="export-section">
            <!-- 导出选项 -->
            <el-form :model="exportForm" label-width="100px">
              <el-form-item label="导出类型">
                <el-radio-group v-model="exportForm.type">
                  <el-radio label="products">商品数据</el-radio>
                  <el-radio label="orders">订单数据</el-radio>
                  <el-radio label="stock_logs">库存流水</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="导出格式">
                <el-radio-group v-model="exportForm.format">
                  <el-radio label="excel">Excel (.xlsx)</el-radio>
                  <el-radio label="csv">CSV (.csv)</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <!-- 商品筛选条件 -->
              <template v-if="exportForm.type === 'products'">
                <el-form-item label="商品分类">
                  <el-select v-model="exportForm.category_id" placeholder="全部分类" clearable>
                    <el-option 
                      v-for="cat in categories" 
                      :key="cat.id" 
                      :label="cat.name" 
                      :value="cat.id"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="库存状态">
                  <el-select v-model="exportForm.stock_status" placeholder="全部" clearable>
                    <el-option label="充足" value="sufficient" />
                    <el-option label="正常" value="normal" />
                    <el-option label="预警" value="warning" />
                    <el-option label="缺货" value="out" />
                  </el-select>
                </el-form-item>
              </template>
              
              <!-- 订单筛选条件 -->
              <template v-if="exportForm.type === 'orders'">
                <el-form-item label="订单状态">
                  <el-select v-model="exportForm.order_status" placeholder="全部状态" clearable>
                    <el-option label="待处理" value="pending" />
                    <el-option label="已完成" value="completed" />
                    <el-option label="已取消" value="cancelled" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="exportForm.date_range"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </template>
            </el-form>
            
            <!-- 导出按钮 -->
            <div class="export-actions">
              <el-button type="primary" @click="handleExport" :loading="exporting">
                <el-icon><Download /></el-icon>
                立即导出
              </el-button>
            </div>
            
            <!-- 导出说明 -->
            <div class="export-tips">
              <h4>导出说明</h4>
              <ul>
                <li>商品数据：包含商品编码、名称、分类、价格、库存等信息</li>
                <li>订单数据：包含订单号、客户信息、商品明细、金额等信息</li>
                <li>库存流水：包含商品名称、变动类型、数量、时间等信息</li>
                <li>Excel格式支持更丰富的样式和格式，CSV格式文件更小</li>
              </ul>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { 
  Upload, 
  Download, 
  UploadFilled,
  CircleClose
} from '@element-plus/icons-vue'

// 数据状态
const categories = ref([])
const importResult = ref(null)
const exporting = ref(false)
const uploadRef = ref()

// 导出表单
const exportForm = reactive({
  type: 'products',
  format: 'excel',
  category_id: null,
  stock_status: null,
  order_status: null,
  date_range: null
})

// 上传配置
const uploadUrl = computed(() => '/api/import/products')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 下载导入模板
async function downloadTemplate() {
  try {
    const res = await axios.get('/api/export/template', {
      responseType: 'blob'
    })
    
    const blob = new Blob([res.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '商品导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败')
  }
}

// 上传前验证
function beforeUpload(file) {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                  file.type === 'application/vnd.ms-excel'
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件！')
    return false
  }
  
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！')
    return false
  }
  
  importResult.value = null
  return true
}

// 上传成功处理
function handleUploadSuccess(response) {
  importResult.value = response
  
  if (response.success_count > 0) {
    ElMessage.success(`成功导入 ${response.success_count} 条数据`)
  }
  
  if (response.error_count > 0) {
    ElMessage.warning(`有 ${response.error_count} 条数据导入失败，请查看错误详情`)
  }
}

// 上传失败处理
function handleUploadError(error) {
  console.error('上传失败:', error)
  ElMessage.error('文件上传失败，请重试')
}

// 导出数据
async function handleExport() {
  exporting.value = true
  
  try {
    let url = ''
    const params = new URLSearchParams()
    
    // 根据导出类型构建URL
    if (exportForm.type === 'products') {
      url = '/api/export/products'
      params.append('format', exportForm.format)
      if (exportForm.category_id) {
        params.append('category_id', exportForm.category_id)
      }
      if (exportForm.stock_status) {
        params.append('stock_status', exportForm.stock_status)
      }
    } else if (exportForm.type === 'orders') {
      url = '/api/export/orders'
      params.append('format', exportForm.format)
      if (exportForm.order_status) {
        params.append('status', exportForm.order_status)
      }
      if (exportForm.date_range) {
        params.append('start_date', exportForm.date_range[0])
        params.append('end_date', exportForm.date_range[1])
      }
    } else if (exportForm.type === 'stock_logs') {
      url = '/api/export/stock-logs'
      params.append('format', exportForm.format)
    }
    
    // 发起导出请求
    const res = await axios.get(`${url}?${params.toString()}`, {
      responseType: 'blob'
    })
    
    // 处理文件下载
    const contentType = exportForm.format === 'excel' 
      ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      : 'text/csv'
    
    const blob = new Blob([res.data], { type: contentType })
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    
    // 设置文件名
    const typeMap = {
      products: '商品数据',
      orders: '订单数据',
      stock_logs: '库存流水'
    }
    const extension = exportForm.format === 'excel' ? 'xlsx' : 'csv'
    link.download = `${typeMap[exportForm.type]}_${new Date().toLocaleDateString()}.${extension}`
    
    link.click()
    window.URL.revokeObjectURL(downloadUrl)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// 获取分类列表
async function fetchCategories() {
  try {
    const res = await axios.get('/api/categories')
    categories.value = res.data
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 初始化
fetchCategories()
</script>

<style scoped>
.import-export-container {
  padding: 0;
}

.import-card,
.export-card {
  border-radius: 8px;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 导入部分样式 */
.import-section {
  padding: 20px 0;
}

.template-section,
.upload-section,
.result-section {
  margin-bottom: 30px;
}

.template-section h4,
.upload-section h4,
.result-section h4 {
  margin-bottom: 15px;
  color: #303133;
}

.tips {
  color: #909399;
  margin-bottom: 15px;
  font-size: 14px;
}

.upload-demo {
  width: 100%;
}

.error-list {
  margin-top: 20px;
  background: #fef0f0;
  padding: 15px;
  border-radius: 4px;
}

.error-list h5 {
  margin-bottom: 10px;
  color: #f56c6c;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  font-size: 14px;
  color: #f56c6c;
}

/* 导出部分样式 */
.export-section {
  padding: 20px 0;
}

.export-actions {
  margin-top: 30px;
  text-align: center;
}

.export-tips {
  margin-top: 40px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.export-tips h4 {
  margin-bottom: 15px;
  color: #303133;
}

.export-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.export-tips li {
  padding-left: 20px;
  margin-bottom: 8px;
  position: relative;
  font-size: 14px;
  color: #606266;
}

.export-tips li::before {
  content: '•';
  position: absolute;
  left: 8px;
  color: #409eff;
}

/* 响应式 */
@media (max-width: 768px) {
  .import-card,
  .export-card {
    margin-bottom: 20px;
  }
}
</style>

