<template>
  <div>
    <el-row justify="space-between" align="middle" style="margin-bottom:16px;">
      <el-col><h2>商品管理</h2></el-col>
      <el-col>
        <el-input v-model="searchName" placeholder="搜索商品名称" style="width:200px;margin-right:8px;" clearable @input="fetchProducts" />
        <el-button type="primary" @click="showAdd=true">新增商品</el-button>
      </el-col>
    </el-row>
    <el-table :data="products" style="width:100%" :border="true" size="large" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="description" label="描述"/>
      <el-table-column prop="price" label="价格"/>
      <el-table-column prop="stock" label="库存"/>
      <el-table-column label="操作" width="260">
        <template #default="{row}">
          <el-button size="small" @click="edit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
          <el-button size="small" type="success" @click="openStockDialog(row, '入库')">入库</el-button>
          <el-button size="small" type="warning" @click="openStockDialog(row, '出库')">出库</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showAdd" title="新增商品" width="400px">
      <el-form :model="form" label-width="60px">
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description"/></el-form-item>
        <el-form-item label="价格"><el-input v-model.number="form.price" type="number"/></el-form-item>
        <el-form-item label="库存"><el-input v-model.number="form.stock" type="number"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd=false">取消</el-button>
        <el-button type="primary" @click="add">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showEdit" title="编辑商品" width="400px">
      <el-form :model="form" label-width="60px">
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description"/></el-form-item>
        <el-form-item label="价格"><el-input v-model.number="form.price" type="number"/></el-form-item>
        <el-form-item label="库存"><el-input v-model.number="form.stock" type="number"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" @click="update">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showStock" :title="stockType + '操作'" width="350px">
      <el-form label-width="60px">
        <el-form-item label="数量">
          <el-input-number v-model="stockNum" :min="1" :max="999999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStock=false">取消</el-button>
        <el-button type="primary" @click="doStock">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
const products = ref([])
const loading = ref(false)
const showAdd = ref(false)
const showEdit = ref(false)
const form = ref({ name: '', description: '', price: 0, stock: 0 })
const editId = ref(null)
const showStock = ref(false)
const stockType = ref('入库')
const stockNum = ref(1)
const stockRow = ref(null)
const searchName = ref('')
async function fetchProducts() {
  loading.value = true
  let url = '/api/products'
  if (searchName.value) url += `?name=${encodeURIComponent(searchName.value)}`
  const res = await axios.get(url)
  products.value = res.data
  loading.value = false
}
onMounted(fetchProducts)
function edit(row) {
  showEdit.value = true
  editId.value = row.id
  form.value = { ...row }
}
function del(row) {
  ElMessageBox.confirm('确定删除该商品吗？', '提示', { type: 'warning' })
    .then(async () => {
      await axios.delete(`/api/products/${row.id}`)
      ElMessage.success('删除成功')
      fetchProducts()
    })
}
async function add() {
  await axios.post('/api/products', form.value)
  ElMessage.success('新增成功')
  showAdd.value = false
  fetchProducts()
}
async function update() {
  await axios.put(`/api/products/${editId.value}`, form.value)
  ElMessage.success('修改成功')
  showEdit.value = false
  fetchProducts()
}
function openStockDialog(row, type) {
  stockRow.value = row
  stockType.value = type
  stockNum.value = 1
  showStock.value = true
}
async function doStock() {
  if (!stockRow.value) return
  await axios.post('/api/stock', {
    product_id: stockRow.value.id,
    change: stockNum.value,
    type: stockType.value
  })
  ElMessage.success(stockType.value + '成功')
  showStock.value = false
  fetchProducts()
}
</script>
<style scoped>
h2 { margin: 0 0 12px 0; }
@media (max-width: 600px) {
  .el-table { font-size: 12px; }
}
</style> 