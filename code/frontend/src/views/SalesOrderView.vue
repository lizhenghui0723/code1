<template>
  <div class="sales-order-container">
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.order_no" placeholder="请输入订单号" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="客户信息">
          <el-input v-model="searchForm.customer" placeholder="客户姓名/电话" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker v-model="searchForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon>搜索</el-button>
          <el-button @click="resetSearch"><el-icon><Refresh /></el-icon>重置</el-button>
        </el-form-item>
      </el-form>
      
      <div class="action-buttons">
        <el-button type="primary" @click="showCreateOrder = true">
          <el-icon><Plus /></el-icon>
          创建订单
        </el-button>
      </div>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="table-card" shadow="never">
      <div class="sort-bar">
        <span class="sort-label">排序：</span>
        <el-radio-group v-model="sortBy" size="small" @change="handleSort">
          <el-radio-button label="created_at">创建时间</el-radio-button>
          <el-radio-button label="total_amount">订单金额</el-radio-button>
        </el-radio-group>
        <el-radio-group v-model="sortOrder" size="small" @change="handleSort" style="margin-left: 20px">
          <el-radio-button label="desc"><el-icon><SortDown /></el-icon>降序</el-radio-button>
          <el-radio-button label="asc"><el-icon><SortUp /></el-icon>升序</el-radio-button>
        </el-radio-group>
      </div>
      <el-table 
        :data="orders" 
        style="width: 100%" 
        v-loading="loading"
        @row-click="viewOrderDetail"
        row-class-name="clickable-row"
        @sort-change="handleTableSort"
      >
        <el-table-column prop="order_no" label="订单号" width="180" sortable="custom" />
        <el-table-column label="客户信息" width="200">
          <template #default="{ row }">
            <div class="customer-info">
              <div>{{ row.customer_name || '散客' }}</div>
              <div class="phone">{{ row.customer_phone || '-' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="商品信息" min-width="300">
          <template #default="{ row }">
            <div class="products-info">
              <el-tag 
                v-for="(item, index) in row.order_items.slice(0, 3)" 
                :key="index"
                size="small"
                style="margin-right: 5px; margin-bottom: 5px"
              >
                {{ item.product.name }} x{{ item.quantity }}
              </el-tag>
              <el-tag v-if="row.order_items.length > 3" size="small" type="info">
                +{{ row.order_items.length - 3 }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="订单金额" width="120" align="right" sortable="custom">
          <template #default="{ row }">
            <span class="amount">¥{{ row.total_amount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="订单状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'" 
              type="success" 
              size="small" 
              @click.stop="completeOrder(row)"
            >
              完成
            </el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              type="danger" 
              size="small" 
              @click.stop="cancelOrder(row)"
            >
              取消
            </el-button>
            <el-button 
              type="primary" 
              size="small" 
              link 
              @click.stop="viewOrderDetail(row)"
            >
              详情
            </el-button>
          </template>
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

    <!-- 创建订单对话框 -->
    <el-dialog 
      v-model="showCreateOrder" 
      title="创建销售订单" 
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="orderForm" ref="orderFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名">
              <el-input v-model="orderForm.customer_name" placeholder="选填" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户电话">
              <el-input v-model="orderForm.customer_phone" placeholder="选填" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="备注">
          <el-input 
            v-model="orderForm.notes" 
            type="textarea" 
            :rows="2"
            placeholder="选填"
          />
        </el-form-item>
        
        <el-divider>商品明细</el-divider>
        
        <!-- 商品选择 -->
        <el-form-item>
          <el-select 
            v-model="selectedProduct" 
            placeholder="请选择商品" 
            filterable
            style="width: 300px; margin-right: 10px"
          >
            <el-option 
              v-for="product in availableProducts" 
              :key="product.id" 
              :label="`${product.name} (库存: ${product.stock})`" 
              :value="product.id"
              :disabled="product.stock === 0"
            />
          </el-select>
          <el-button type="primary" @click="addProduct" :disabled="!selectedProduct">
            添加商品
          </el-button>
        </el-form-item>
        
        <!-- 已选商品列表 -->
        <el-table :data="orderForm.items" style="width: 100%" show-summary :summary-method="getSummaries">
          <el-table-column prop="product.name" label="商品名称" />
          <el-table-column label="单价" width="120">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.unit_price" 
                :min="0" 
                :precision="2"
                size="small"
                @change="calculateTotal"
              />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="150">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.quantity" 
                :min="1" 
                :max="row.product.stock"
                size="small"
                @change="calculateTotal"
              />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120" align="right">
            <template #default="{ row }">
              ¥{{ (row.unit_price * row.quantity).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row, $index }">
              <el-button type="danger" size="small" link @click="removeProduct($index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty v-if="!orderForm.items.length" description="请添加商品" />
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateOrder = false">取消</el-button>
        <el-button type="primary" @click="createOrder" :disabled="!orderForm.items.length">
          创建订单
        </el-button>
      </template>
    </el-dialog>

    <!-- 订单详情对话框 -->
    <el-dialog 
      v-model="showOrderDetail" 
      title="订单详情" 
      width="700px"
    >
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单号">
          {{ currentOrder.order_no }}
        </el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="客户姓名">
          {{ currentOrder.customer_name || '散客' }}
        </el-descriptions-item>
        <el-descriptions-item label="客户电话">
          {{ currentOrder.customer_phone || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="订单金额">
          <span class="amount">¥{{ currentOrder.total_amount.toFixed(2) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatTime(currentOrder.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentOrder.notes || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider>商品明细</el-divider>
      
      <el-table :data="currentOrder?.order_items" style="width: 100%">
        <el-table-column prop="product.name" label="商品名称" />
        <el-table-column prop="unit_price" label="单价" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.unit_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column prop="total_price" label="小计" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.total_price.toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { Search, Refresh, Plus, SortDown, SortUp } from '@element-plus/icons-vue'

// 数据状态
const orders = ref([])
const products = ref([])
const loading = ref(false)
const showCreateOrder = ref(false)
const showOrderDetail = ref(false)
const currentOrder = ref(null)
const selectedProduct = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const sortBy = ref('created_at')
const sortOrder = ref('desc')

// 搜索表单
const searchForm = reactive({
  order_no: '',
  customer: '',
  status: '',
  dateRange: []
})

// 订单表单
const orderFormRef = ref()
const orderForm = reactive({
  customer_name: '',
  customer_phone: '',
  notes: '',
  items: []
})

// 计算可用商品（有库存的）
const availableProducts = ref([])

// 获取订单列表
async function fetchOrders() {
  loading.value = true
  try {
    const res = await axios.get('/api/sales-orders', { params: {
      order_no: searchForm.order_no,
      customer: searchForm.customer,
      status: searchForm.status,
      start_time: searchForm.dateRange && searchForm.dateRange[0],
      end_time: searchForm.dateRange && searchForm.dateRange[1],
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      page: currentPage.value,
      page_size: pageSize.value
    } })
    orders.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 获取商品列表
async function fetchProducts() {
  try {
    const res = await axios.get('/api/products')
    products.value = res.data
    availableProducts.value = res.data.filter(p => p.stock > 0)
  } catch (error) {
    console.error('获取商品列表失败:', error)
  }
}

// 重置搜索
function resetSearch() {
  searchForm.order_no = ''
  searchForm.customer = ''
  searchForm.status = ''
  searchForm.dateRange = []
  fetchOrders()
}

// 添加商品到订单
function addProduct() {
  const product = products.value.find(p => p.id === selectedProduct.value)
  if (!product) return
  
  // 检查是否已添加
  const existing = orderForm.items.find(item => item.product_id === product.id)
  if (existing) {
    ElMessage.warning('该商品已添加')
    return
  }
  
  orderForm.items.push({
    product_id: product.id,
    product: product,
    unit_price: product.price,
    quantity: 1
  })
  
  selectedProduct.value = null
  calculateTotal()
}

// 移除商品
function removeProduct(index) {
  orderForm.items.splice(index, 1)
  calculateTotal()
}

// 计算总计
function calculateTotal() {
  // 触发表格更新
}

// 获取汇总数据
function getSummaries(param) {
  const { columns, data } = param
  const sums = []
  
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '合计'
      return
    }
    
    if (column.property === 'quantity') {
      const values = data.map(item => Number(item.quantity))
      sums[index] = values.reduce((prev, curr) => prev + curr, 0)
    } else if (index === columns.length - 2) { // 小计列
      const values = data.map(item => item.unit_price * item.quantity)
      const total = values.reduce((prev, curr) => prev + curr, 0)
      sums[index] = `¥${total.toFixed(2)}`
    } else {
      sums[index] = ''
    }
  })
  
  return sums
}

// 创建订单
async function createOrder() {
  if (!orderForm.items.length) {
    ElMessage.warning('请添加商品')
    return
  }
  
  try {
    const data = {
      customer_name: orderForm.customer_name,
      customer_phone: orderForm.customer_phone,
      notes: orderForm.notes,
      items: orderForm.items.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price
      }))
    }
    
    await axios.post('/api/sales-orders', data)
    ElMessage.success('订单创建成功')
    showCreateOrder.value = false
    
    // 重置表单
    orderForm.customer_name = ''
    orderForm.customer_phone = ''
    orderForm.notes = ''
    orderForm.items = []
    
    // 刷新列表
    fetchOrders()
    fetchProducts() // 刷新商品库存
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建订单失败')
  }
}

// 完成订单
function completeOrder(order) {
  ElMessageBox.confirm(
    '确定要完成该订单吗？',
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(async () => {
    try {
      await axios.put(`/api/sales-orders/${order.id}`, { status: 'completed' })
      ElMessage.success('订单已完成')
      fetchOrders()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  })
}

// 取消订单
function cancelOrder(order) {
  ElMessageBox.confirm(
    '确定要取消该订单吗？取消后库存将恢复。',
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await axios.put(`/api/sales-orders/${order.id}`, { status: 'cancelled' })
      ElMessage.success('订单已取消')
      fetchOrders()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  })
}

// 查看订单详情
function viewOrderDetail(order) {
  currentOrder.value = order
  showOrderDetail.value = true
}

// 获取状态类型
function getStatusType(status) {
  const map = {
    pending: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

// 获取状态文本
function getStatusText(status) {
  const map = {
    pending: '待处理',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 格式化时间
function formatTime(time) {
  return new Date(time).toLocaleString('zh-CN')
}

// 处理搜索
function handleSearch() {
  currentPage.value = 1
  fetchOrders()
}

// 处理排序
function handleSort() {
  currentPage.value = 1
  fetchOrders()
}

// 处理表格排序
function handleTableSort(event) {
  if (event.column) {
    sortBy.value = event.column.property
    sortOrder.value = event.order === 'ascending' ? 'asc' : 'desc'
    currentPage.value = 1
    fetchOrders()
  }
}

// 处理分页
function handleSizeChange(newSize) {
  pageSize.value = newSize
  currentPage.value = 1
  fetchOrders()
}

function handlePageChange(newPage) {
  currentPage.value = newPage
  fetchOrders()
}

// 初始化
onMounted(() => {
  fetchOrders()
  fetchProducts()
})
</script>

<style scoped>
.sales-order-container {
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

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background-color: #f5f7fa;
}

.order-no {
  color: #409eff;
  font-weight: 500;
}

.customer-info {
  line-height: 1.5;
}

.customer-info .phone {
  font-size: 12px;
  color: #909399;
}

.products-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.amount {
  color: #f56c6c;
  font-weight: 500;
  font-size: 16px;
}

.sort-bar {
  margin-bottom: 20px;
}

.sort-label {
  margin-right: 10px;
}

/* 响应式 */
@media (max-width: 768px) {
  .search-form .el-form-item {
    margin-bottom: 10px;
  }
}
</style>

