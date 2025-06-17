<template>
  <div class="product-list-container">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="商品名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入商品名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select 
            v-model="searchForm.category_id" 
            placeholder="全部分类"
            clearable
            style="width: 150px"
          >
            <el-option 
              v-for="cat in categories" 
              :key="cat.id" 
              :label="cat.name" 
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格区间">
          <el-input-number 
            v-model="searchForm.min_price" 
            :min="0" 
            :precision="2"
            placeholder="最低价"
            style="width: 120px"
          />
          <span style="margin: 0 10px">-</span>
          <el-input-number 
            v-model="searchForm.max_price" 
            :min="0" 
            :precision="2"
            placeholder="最高价"
            style="width: 120px"
          />
        </el-form-item>
        <el-form-item label="库存状态">
          <el-select 
            v-model="stockFilter" 
            placeholder="全部"
            clearable
            style="width: 120px"
            @change="handleStockFilter"
          >
            <el-option label="充足" value="sufficient" />
            <el-option label="正常" value="normal" />
            <el-option label="预警" value="warning" />
            <el-option label="缺货" value="out" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button type="primary" @click="showAdd = true">
          <el-icon><Plus /></el-icon>
          新增商品
        </el-button>
        <el-button type="success" @click="$parent.handleMenu('import-export')">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="exportProducts">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </el-card>

    <!-- 商品列表 -->
    <el-card class="table-card" shadow="never">
      <!-- 排序选项 -->
      <div class="sort-bar">
        <span class="sort-label">排序：</span>
        <el-radio-group v-model="sortBy" size="small" @change="handleSort">
          <el-radio-button label="created_at">创建时间</el-radio-button>
          <el-radio-button label="price">价格</el-radio-button>
          <el-radio-button label="stock">库存</el-radio-button>
          <el-radio-button label="sales_count">销量</el-radio-button>
        </el-radio-group>
        <el-radio-group v-model="sortOrder" size="small" @change="handleSort" style="margin-left: 20px">
          <el-radio-button label="desc">
            <el-icon><SortDown /></el-icon>
            降序
          </el-radio-button>
          <el-radio-button label="asc">
            <el-icon><SortUp /></el-icon>
            升序
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 数据表格 -->
      <el-table 
        :data="products" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="sku" label="商品编码" width="150" />
        <el-table-column prop="name" label="商品名称" min-width="200">
          <template #default="{ row }">
            <div class="product-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.category" size="small" type="info" style="margin-left: 8px">
                {{ row.category.name }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="销售价格" width="120" align="right">
          <template #default="{ row }">
            <span class="price">¥{{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本价格" width="120" align="right">
          <template #default="{ row }">
            <span>¥{{ row.cost_price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="当前库存" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStockType(row)" effect="plain">
              {{ row.stock }} {{ row.unit }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sales_count" label="累计销量" width="100" align="center" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="edit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="del(row)">删除</el-button>
            <el-button size="small" type="success" @click="openStockDialog(row, '入库')">入库</el-button>
            <el-button size="small" type="warning" @click="openStockDialog(row, '出库')">出库</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      v-model="showAdd" 
      :title="editId ? '编辑商品' : '新增商品'" 
      width="600px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="商品分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option 
              v-for="cat in categories" 
              :key="cat.id" 
              :label="cat.name" 
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品编码">
          <el-input v-model="form.sku" placeholder="不填写将自动生成" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="销售价格" prop="price">
              <el-input-number 
                v-model="form.price" 
                :min="0" 
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本价格">
              <el-input-number 
                v-model="form.cost_price" 
                :min="0" 
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="当前库存" prop="stock">
              <el-input-number 
                v-model="form.stock" 
                :min="0"
                style="width: 420px"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低库存">
              <el-input-number 
                v-model="form.min_stock" 
                :min="0"
                style="width: 220px"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="计量单位">
              <el-input v-model="form.unit" placeholder="件/个/箱" style="width: 220px" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="商品描述">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入商品描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 库存调整对话框 -->
    <el-dialog 
      v-model="showStock" 
      :title="stockType + '操作'" 
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="商品名称">
          <el-input :value="stockProduct?.name" disabled />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input :value="`${stockProduct?.stock} ${stockProduct?.unit}`" disabled />
        </el-form-item>
        <el-form-item label="调整数量">
          <el-input-number 
            v-model="stockNum" 
            :min="1" 
            :max="stockType === '出库' ? stockProduct?.stock : 999999"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockRemark" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStock = false">取消</el-button>
        <el-button type="primary" @click="doStock">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { 
  Search, 
  Refresh, 
  Plus, 
  Upload, 
  Download,
  SortDown,
  SortUp
} from '@element-plus/icons-vue'

// 数据状态
const products = ref([])
const categories = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedProducts = ref([])

// 搜索表单
const searchForm = reactive({
  name: '',
  category_id: null,
  min_price: null,
  max_price: null,
  min_stock: null,
  max_stock: null
})

// 排序
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const stockFilter = ref('')

// 对话框
const showAdd = ref(false)
const editId = ref(null)
const formRef = ref()
const form = reactive({
  name: '',
  description: '',
  price: 0,
  cost_price: 0,
  stock: 0,
  min_stock: 10,
  unit: '件',
  category_id: null,
  sku: ''
})

// 库存调整
const showStock = ref(false)
const stockType = ref('入库')
const stockNum = ref(1)
const stockProduct = ref(null)
const stockRemark = ref('')

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入销售价格', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入当前库存', trigger: 'blur' }
  ]
}

// 获取商品列表
async function fetchProducts() {
  loading.value = true
  try {
    // 构建查询参数
    const query = {
      ...searchForm,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const res = await axios.post('/api/products/query', query)
    products.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
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

// 搜索
function handleSearch() {
  currentPage.value = 1
  fetchProducts()
}

// 重置搜索
function resetSearch() {
  searchForm.name = ''
  searchForm.category_id = null
  searchForm.min_price = null
  searchForm.max_price = null
  searchForm.min_stock = null
  searchForm.max_stock = null
  stockFilter.value = ''
  handleSearch()
}

// 库存筛选
function handleStockFilter(value) {
  if (value === 'sufficient') {
    searchForm.min_stock = 21
    searchForm.max_stock = null
  } else if (value === 'normal') {
    searchForm.min_stock = 11
    searchForm.max_stock = 20
  } else if (value === 'warning') {
    searchForm.min_stock = 1
    searchForm.max_stock = 10
  } else if (value === 'out') {
    searchForm.min_stock = 0
    searchForm.max_stock = 0
  } else {
    searchForm.min_stock = null
    searchForm.max_stock = null
  }
  handleSearch()
}

// 排序
function handleSort() {
  fetchProducts()
}

// 分页
function handleSizeChange() {
  currentPage.value = 1
  fetchProducts()
}

function handlePageChange() {
  fetchProducts()
}

// 选择变化
function handleSelectionChange(selection) {
  selectedProducts.value = selection
}

// 编辑商品
function edit(row) {
  showAdd.value = true
  editId.value = row.id
  Object.assign(form, row)
}

// 删除商品
function del(row) {
  ElMessageBox.confirm(
    `确定要删除商品"${row.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.delete(`/api/products/${row.id}`)
      ElMessage.success('删除成功')
      fetchProducts()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
async function handleSubmit() {
  await formRef.value.validate()
  
  try {
    if (editId.value) {
      await axios.put(`/api/products/${editId.value}`, form)
      ElMessage.success('修改成功')
    } else {
      await axios.post('/api/products', form)
      ElMessage.success('新增成功')
    }
    showAdd.value = false
    fetchProducts()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 打开库存调整对话框
function openStockDialog(row, type) {
  stockProduct.value = row
  stockType.value = type
  stockNum.value = 1
  stockRemark.value = ''
  showStock.value = true
}

// 执行库存调整
async function doStock() {
  if (!stockProduct.value) return
  
  try {
    await axios.post('/api/stock', {
      product_id: stockProduct.value.id,
      change: stockNum.value,
      type: stockType.value,
      reference_no: stockRemark.value
    })
    ElMessage.success(stockType.value + '成功')
    showStock.value = false
    fetchProducts()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 导出商品
async function exportProducts() {
  try {
    const res = await axios.get('/api/export/products', {
      responseType: 'blob'
    })
    
    const blob = new Blob([res.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `商品数据_${new Date().toLocaleDateString()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 获取库存状态类型
function getStockType(row) {
  if (row.stock === 0) return 'danger'
  if (row.stock <= row.min_stock) return 'warning'
  if (row.stock > row.min_stock * 2) return 'success'
  return ''
}

// 初始化
onMounted(() => {
  fetchProducts()
  fetchCategories()
})

// 重置表单
function resetForm() {
  editId.value = null
  form.name = ''
  form.description = ''
  form.price = 0
  form.cost_price = 0
  form.stock = 0
  form.min_stock = 10
  form.unit = '件'
  form.category_id = null
  form.sku = ''
  formRef.value?.resetFields()
}
</script>

<style scoped>
.product-list-container {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.search-form {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
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

.product-name {
  display: flex;
  align-items: center;
}

.price {
  color: #f56c6c;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 768px) {
  .search-form .el-form-item {
    margin-bottom: 10px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style> 