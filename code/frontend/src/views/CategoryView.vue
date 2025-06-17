<template>
  <div class="category-view">
    <el-card class="category-card">
          <template #header>
            <div class="card-header">
          <span>商品分类管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>添加分类
              </el-button>
            </div>
          </template>
      <!-- 分类列表 -->
      <el-table :data="categories" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
                <template #default="{ row }">
            {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
            <el-button type="primary" size="small" @click="showEditDialog(row)"><el-icon><Edit /></el-icon>编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)"><el-icon><Delete /></el-icon>删除</el-button>
                </template>
              </el-table-column>
            </el-table>
      <el-empty v-if="!categories.length && !loading" description="暂无分类" />
        </el-card>
    <!-- 添加/编辑分类对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="400px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入分类描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

// 分类数据
const categories = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)
const formRef = ref()

// 表单数据
const form = ref({
  id: null,
  name: '',
  description: ''
})

// 表单校验规则
const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }
  ]
}

// 获取分类列表
async function fetchCategories() {
  loading.value = true
  try {
    const res = await axios.get('/api/categories')
    categories.value = res.data
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
function showAddDialog() {
  dialogTitle.value = '添加分类'
  form.value = { id: null, name: '', description: '' }
  dialogVisible.value = true
}

// 显示编辑对话框
function showEditDialog(row) {
  dialogTitle.value = '编辑分类'
  form.value = { ...row }
  dialogVisible.value = true
}

// 重置表单
function resetForm() {
  if (formRef.value) formRef.value.resetFields()
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (form.value.id) {
          // 编辑
          await axios.put(`/api/categories/${form.value.id}`, form.value)
          ElMessage.success('分类更新成功')
        } else {
          // 新增
          await axios.post('/api/categories', form.value)
          ElMessage.success('分类添加成功')
        }
        dialogVisible.value = false
      fetchCategories()
    } catch (error) {
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 删除分类
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该分类吗？删除后无法恢复。', '警告', { type: 'warning' })
    await axios.delete(`/api/categories/${row.id}`)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

// 格式化时间
function formatTime(date) {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-view {
  padding: 20px;
}
.category-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

