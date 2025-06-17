<template>
  <div class="sales-report-container">
    <!-- 时间筛选 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="dateShortcuts"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="统计维度">
          <el-radio-group v-model="filterForm.dimension" @change="fetchReportData">
            <el-radio-button label="day">按日</el-radio-button>
            <el-radio-button label="week">按周</el-radio-button>
            <el-radio-button label="month">按月</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-value">¥{{ formatNumber(summaryData.totalSales) }}</div>
            <div class="stat-label">销售总额</div>
            <div class="stat-trend" :class="summaryData.salesTrend >= 0 ? 'up' : 'down'">
              <el-icon>
                <component :is="summaryData.salesTrend >= 0 ? 'TrendCharts' : 'TrendCharts'" />
              </el-icon>
              {{ Math.abs(summaryData.salesTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-value">{{ summaryData.totalOrders }}</div>
            <div class="stat-label">订单数量</div>
            <div class="stat-trend" :class="summaryData.ordersTrend >= 0 ? 'up' : 'down'">
              <el-icon>
                <component :is="summaryData.ordersTrend >= 0 ? 'TrendCharts' : 'TrendCharts'" />
              </el-icon>
              {{ Math.abs(summaryData.ordersTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-value">¥{{ formatNumber(summaryData.avgOrderValue) }}</div>
            <div class="stat-label">客单价</div>
            <div class="stat-trend" :class="summaryData.avgTrend >= 0 ? 'up' : 'down'">
              <el-icon>
                <component :is="summaryData.avgTrend >= 0 ? 'TrendCharts' : 'TrendCharts'" />
              </el-icon>
              {{ Math.abs(summaryData.avgTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-value">{{ summaryData.totalProducts }}</div>
            <div class="stat-label">销售商品数</div>
            <div class="stat-trend" :class="summaryData.productsTrend >= 0 ? 'up' : 'down'">
              <el-icon>
                <component :is="summaryData.productsTrend >= 0 ? 'TrendCharts' : 'TrendCharts'" />
              </el-icon>
              {{ Math.abs(summaryData.productsTrend) }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <!-- 销售趋势图 -->
      <el-col :span="24">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <span class="card-title">销售趋势分析</span>
          </template>
          <div class="chart-container">
            <v-chart :option="salesTrendOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <!-- 商品销售排行 -->
      <el-col :xs="24" :md="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="card-title">商品销售TOP10</span>
              <el-radio-group v-model="productRankType" size="small" @change="fetchProductRank">
                <el-radio-button label="quantity">按数量</el-radio-button>
                <el-radio-button label="amount">按金额</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="productRankOption" autoresize />
          </div>
        </el-card>
      </el-col>

      <!-- 分类销售分布 -->
      <el-col :xs="24" :md="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <span class="card-title">分类销售分布</span>
          </template>
          <div class="chart-container">
            <v-chart :option="categorySalesOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">销售明细数据</span>
          <el-button type="primary" @click="exportReport">
            <el-icon><Download /></el-icon>
            导出报表
          </el-button>
        </div>
      </template>
      
      <el-table :data="detailData" style="width: 100%" v-loading="loading">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="orderCount" label="订单数" width="100" align="center" />
        <el-table-column prop="productCount" label="商品数" width="100" align="center" />
        <el-table-column prop="totalAmount" label="销售额" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.totalAmount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="avgAmount" label="客单价" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.avgAmount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="热销商品" min-width="200">
          <template #default="{ row }">
            <el-tag 
              v-for="product in row.topProducts.slice(0, 3)" 
              :key="product.name"
              size="small"
              style="margin-right: 5px"
            >
              {{ product.name }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Download, TrendCharts } from '@element-plus/icons-vue'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent
])

// 数据状态
const loading = ref(false)
const filterForm = reactive({
  dateRange: [],
  dimension: 'day'
})

// 汇总数据
const summaryData = reactive({
  totalSales: 0,
  totalOrders: 0,
  avgOrderValue: 0,
  totalProducts: 0,
  salesTrend: 0,
  ordersTrend: 0,
  avgTrend: 0,
  productsTrend: 0
})

// 图表数据
const salesTrendData = ref([])
const productRankData = ref([])
const categorySalesData = ref([])
const detailData = ref([])
const productRankType = ref('quantity')

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  },
  {
    text: '本月',
    value: () => {
      const end = new Date()
      const start = new Date(end.getFullYear(), end.getMonth(), 1)
      return [start, end]
    }
  },
  {
    text: '上月',
    value: () => {
      const end = new Date()
      const start = new Date(end.getFullYear(), end.getMonth() - 1, 1)
      end.setDate(0)
      return [start, end]
    }
  }
]

// 销售趋势图配置
const salesTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  legend: {
    data: ['销售额', '订单数', '客单价']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    containLabel: true
  },
  dataZoom: [
    {
      type: 'inside',
      start: 0,
      end: 100
    },
    {
      start: 0,
      end: 100
    }
  ],
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
      data: salesTrendData.value.map(item => item.totalAmount),
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
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
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
      data: salesTrendData.value.map(item => item.orderCount),
      itemStyle: {
        color: '#f093fb'
      }
    },
    {
      name: '客单价',
      type: 'line',
      smooth: true,
      data: salesTrendData.value.map(item => item.avgAmount),
      itemStyle: {
        color: '#4facfe'
      }
    }
  ]
}))

// 商品销售排行图配置
const productRankOption = computed(() => ({
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
    type: 'value',
    axisLabel: {
      formatter: productRankType.value === 'amount' ? '¥{value}' : '{value}'
    }
  },
  yAxis: {
    type: 'category',
    data: productRankData.value.map(item => item.name),
    axisLabel: {
      width: 80,
      overflow: 'truncate'
    }
  },
  series: [
    {
      name: productRankType.value === 'amount' ? '销售额' : '销售量',
      type: 'bar',
      data: productRankData.value.map(item => 
        productRankType.value === 'amount' ? item.amount : item.quantity
      ),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        },
        borderRadius: [0, 4, 4, 0]
      }
    }
  ]
}))

// 分类销售分布图配置
const categorySalesOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
  },
  legend: {
    type: 'scroll',
    orient: 'vertical',
    right: 10,
    top: 20,
    bottom: 20
  },
  series: [
    {
      name: '分类销售',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
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
      data: categorySalesData.value
    }
  ]
}))

// 获取报表数据
async function fetchReportData() {
  if (!filterForm.dateRange || filterForm.dateRange.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }
  
  loading.value = true
  
  try {
    // 模拟获取数据
    // 实际应该调用后端API
    await Promise.all([
      fetchSummaryData(),
      fetchSalesTrend(),
      fetchProductRank(),
      fetchCategorySales(),
      fetchDetailData()
    ])
  } catch (error) {
    ElMessage.error('获取报表数据失败')
  } finally {
    loading.value = false
  }
}

// 获取汇总数据
async function fetchSummaryData() {
  // 模拟数据
  summaryData.totalSales = 125680.50
  summaryData.totalOrders = 256
  summaryData.avgOrderValue = 490.94
  summaryData.totalProducts = 89
  summaryData.salesTrend = 12.5
  summaryData.ordersTrend = 8.3
  summaryData.avgTrend = 3.2
  summaryData.productsTrend = -2.1
}

// 获取销售趋势
async function fetchSalesTrend() {
  // 模拟数据
  const days = 30
  const data = []
  const now = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    data.push({
      date: date.toLocaleDateString('zh-CN'),
      totalAmount: Math.random() * 5000 + 2000,
      orderCount: Math.floor(Math.random() * 20 + 5),
      avgAmount: Math.random() * 500 + 200
    })
  }
  
  salesTrendData.value = data
}

// 获取商品销售排行
async function fetchProductRank() {
  // 模拟数据
  const products = [
    { name: 'iPhone 14 Pro', quantity: 156, amount: 1248000 },
    { name: 'MacBook Pro 16"', quantity: 89, amount: 1780000 },
    { name: 'iPad Air', quantity: 234, amount: 1404000 },
    { name: 'AirPods Pro', quantity: 456, amount: 1140000 },
    { name: 'Apple Watch Series 8', quantity: 178, amount: 712000 },
    { name: 'Mac mini', quantity: 67, amount: 469000 },
    { name: 'iPhone 13', quantity: 298, amount: 1788000 },
    { name: 'MacBook Air', quantity: 145, amount: 1450000 },
    { name: 'iPad mini', quantity: 189, amount: 945000 },
    { name: 'HomePod mini', quantity: 234, amount: 234000 }
  ]
  
  // 根据类型排序
  productRankData.value = products
    .sort((a, b) => {
      return productRankType.value === 'amount' 
        ? b.amount - a.amount 
        : b.quantity - a.quantity
    })
    .slice(0, 10)
    .reverse() // 反转以适应横向柱状图
}

// 获取分类销售数据
async function fetchCategorySales() {
  // 模拟数据
  categorySalesData.value = [
    { name: '手机数码', value: 3456000 },
    { name: '电脑办公', value: 2890000 },
    { name: '家用电器', value: 1567000 },
    { name: '服装鞋帽', value: 1234000 },
    { name: '食品饮料', value: 987000 },
    { name: '其他', value: 456000 }
  ]
}

// 获取详细数据
async function fetchDetailData() {
  // 模拟数据
  const data = []
  const days = 7
  const now = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    data.push({
      date: date.toLocaleDateString('zh-CN'),
      orderCount: Math.floor(Math.random() * 50 + 10),
      productCount: Math.floor(Math.random() * 30 + 5),
      totalAmount: Math.random() * 10000 + 5000,
      avgAmount: Math.random() * 500 + 200,
      topProducts: [
        { name: 'iPhone 14 Pro' },
        { name: 'MacBook Pro' },
        { name: 'iPad Air' }
      ]
    })
  }
  
  detailData.value = data
}

// 处理日期变化
function handleDateChange() {
  if (filterForm.dateRange && filterForm.dateRange.length === 2) {
    fetchReportData()
  }
}

// 导出报表
async function exportReport() {
  try {
    ElMessage.success('报表导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 格式化数字
function formatNumber(num) {
  return num?.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') || '0.00'
}

// 初始化
onMounted(() => {
  // 设置默认时间范围为最近30天
  const end = new Date()
  const start = new Date()
  start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
  filterForm.dateRange = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]
  
  fetchReportData()
})
</script>

<style scoped>
.sales-report-container {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  border: none;
}

.stat-content {
  position: relative;
  padding: 10px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
}

.stat-trend.up {
  color: #67c23a;
}

.stat-trend.down {
  color: #f56c6c;
}

/* 图表卡片 */
.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
  border: none;
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
  height: 400px;
  padding: 20px 0;
}

/* 表格卡片 */
.table-card {
  border-radius: 12px;
  border: none;
}

/* 响应式 */
@media (max-width: 768px) {
  .stat-value {
    font-size: 24px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>

