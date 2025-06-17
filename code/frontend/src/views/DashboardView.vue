<template>
  <div class="dashboard-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="30"><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_products }}</div>
              <div class="stat-label">商品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon :size="30"><ShoppingCart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_orders }}</div>
              <div class="stat-label">订单总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon :size="30"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ formatNumber(stats.total_sales) }}</div>
              <div class="stat-label">销售总额</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
              <el-icon :size="30"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.low_stock_products }}</div>
              <div class="stat-label">库存预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 销售趋势图 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">销售趋势</span>
              <el-radio-group v-model="trendDays" size="small" @change="fetchSalesTrend">
                <el-radio-button :label="7">7天</el-radio-button>
                <el-radio-button :label="30">30天</el-radio-button>
                <el-radio-button :label="90">90天</el-radio-button>
              </el-radio-group>
            </div>
        </template>
          <div class="chart-container">
            <v-chart :option="salesTrendOption" autoresize />
          </div>
        </el-card>
      </el-col>
      
      <!-- 库存状态饼图 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <span class="card-title">库存状态分布</span>
      </template>
          <div class="chart-container">
            <v-chart :option="stockStatusOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分类销售和最新订单 -->
    <el-row :gutter="20" class="bottom-row">
      <!-- 分类销售统计 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <span class="card-title">分类销售统计</span>
      </template>
          <div class="chart-container">
            <v-chart :option="categorySalesOption" autoresize />
          </div>
        </el-card>
      </el-col>
      
      <!-- 最新订单 -->
      <el-col :xs="24" :lg="12">
        <el-card class="order-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">最新订单</span>
              <el-button type="primary" link @click="$parent.handleMenu('sales-order')">
                查看全部
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </div>
      </template>
          <div class="order-list">
            <div v-for="order in stats.recent_orders" :key="order.id" class="order-item">
              <div class="order-header">
                <span class="order-no">{{ order.order_no }}</span>
                <el-tag :type="getOrderStatusType(order.status)" size="small">
                  {{ getOrderStatusText(order.status) }}
                </el-tag>
              </div>
              <div class="order-info">
                <span class="order-customer">{{ order.customer_name || '散客' }}</span>
                <span class="order-amount">¥{{ order.total_amount }}</span>
              </div>
              <div class="order-time">{{ formatTime(order.created_at) }}</div>
            </div>
            <el-empty v-if="!stats.recent_orders?.length" description="暂无订单" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { 
  Goods, 
  ShoppingCart, 
  Money, 
  Warning, 
  ArrowRight 
} from '@element-plus/icons-vue'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent
])

// 数据状态
const stats = ref({
  total_products: 0,
  total_categories: 0,
  total_orders: 0,
  total_sales: 0,
  low_stock_products: 0,
  today_sales: 0,
  month_sales: 0,
  recent_orders: []
})

const trendDays = ref(7)
const salesTrendData = ref([])
const stockStatusData = ref([])
const categorySalesData = ref([])

// 销售趋势图配置
const salesTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  legend: {
    data: ['销售额', '订单数']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: salesTrendData.value.map(item => item.date)
  },
  yAxis: [
    {
      type: 'value',
      name: '销售额',
      position: 'left',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    {
      type: 'value',
      name: '订单数',
      position: 'right'
    }
  ],
  series: [
    {
      name: '销售额',
      type: 'line',
      smooth: true,
      data: salesTrendData.value.map(item => item.total_amount),
      itemStyle: {
        color: '#667eea'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0)' }
          ]
        }
      }
    },
    {
      name: '订单数',
      type: 'line',
      smooth: true,
      yAxisIndex: 1,
      data: salesTrendData.value.map(item => item.order_count),
      itemStyle: {
        color: '#f093fb'
      }
    }
  ]
}))

// 库存状态饼图配置
const stockStatusOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '库存状态',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '20',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: stockStatusData.value.map(item => ({
        value: item.value,
        name: item.name,
        itemStyle: { color: item.color }
      }))
    }
  ]
}))

// 分类销售柱状图配置
const categorySalesOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: categorySalesData.value.map(item => item.name),
    axisTick: {
      alignWithLabel: true
    },
    axisLabel: {
      rotate: 45
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '¥{value}'
    }
  },
  series: [
    {
      name: '销售额',
      type: 'bar',
      barWidth: '60%',
      data: categorySalesData.value.map(item => item.amount),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#4facfe' },
            { offset: 1, color: '#00f2fe' }
          ]
        },
        borderRadius: [8, 8, 0, 0]
      }
    }
  ]
}))

// 获取统计数据
async function fetchStats() {
  try {
    const res = await axios.get('/api/dashboard/stats')
    stats.value = res.data
  } catch (error) {
    ElMessage.error('获取统计数据失败')
}
}

// 获取销售趋势
async function fetchSalesTrend() {
  try {
    const res = await axios.get(`/api/dashboard/sales-trend?days=${trendDays.value}`)
    salesTrendData.value = res.data
  } catch (error) {
    ElMessage.error('获取销售趋势失败')
  }
}

// 获取库存状态
async function fetchStockStatus() {
  try {
    const res = await axios.get('/api/dashboard/stock-status')
    stockStatusData.value = res.data
  } catch (error) {
    ElMessage.error('获取库存状态失败')
}
}

// 获取分类销售
async function fetchCategorySales() {
  try {
    const res = await axios.get('/api/dashboard/category-sales')
    categorySalesData.value = res.data
  } catch (error) {
    ElMessage.error('获取分类销售失败')
  }
}

// 格式化数字
function formatNumber(num) {
  return num?.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') || '0.00'
}

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

// 获取订单状态类型
function getOrderStatusType(status) {
  const map = {
    pending: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

// 获取订单状态文本
function getOrderStatusText(status) {
  const map = {
    pending: '待处理',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 初始化
onMounted(() => {
  fetchStats()
  fetchSalesTrend()
  fetchStockStatus()
  fetchCategorySales()
  
  // 定时刷新
  setInterval(() => {
    fetchStats()
    fetchSalesTrend()
  }, 60000)
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

/* 统计卡片样式 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 图表卡片样式 */
.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
  border: none;
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.chart-container {
  height: 320px;
  padding: 20px 0;
}

/* 订单列表样式 */
.order-card {
  border-radius: 12px;
  border: none;
  height: 400px;
}

.order-list {
  height: 320px;
  overflow-y: auto;
}

.order-item {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.3s;
}

.order-item:hover {
  background: #f5f7fa;
}

.order-item:last-child {
  border-bottom: none;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.order-no {
  font-weight: 500;
  color: #303133;
}

.order-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.order-customer {
  color: #606266;
  font-size: 14px;
}

.order-amount {
  color: #f56c6c;
  font-weight: 500;
}

.order-time {
  color: #909399;
  font-size: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .stat-value {
    font-size: 24px;
  }
  
  .chart-card {
    height: 350px;
  }
  
  .chart-container {
    height: 280px;
  }
}

/* 美化滚动条 */
.order-list::-webkit-scrollbar {
  width: 6px;
}

.order-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.order-list::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.order-list::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style> 