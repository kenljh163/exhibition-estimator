<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">产品库管理</h1>
      <el-button type="primary" @click="showDialog()"><el-icon><Plus /></el-icon> 新增产品</el-button>
    </div>
    <div class="filter-bar">
      <el-input v-model="filters.keyword" placeholder="搜索产品名称" style="width:200px" clearable @clear="loadData" @keyup.enter="loadData" />
      <el-button @click="loadData">搜索</el-button>
    </div>
    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="name" label="产品名称" min-width="160" />
      <el-table-column prop="category" label="类别" width="100" />
      <el-table-column prop="brand" label="品牌" width="100" />
      <el-table-column prop="model" label="型号" width="120" />
      <el-table-column label="单价(元)" width="100">
        <template #default="{ row }">¥{{ row.unit_price?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="60" />
      <el-table-column prop="lead_time_days" label="供货周期" width="90">
        <template #default="{ row }">{{ row.lead_time_days }}天</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > pageSize" layout="total, prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="loadData" style="margin-top:16px;justify-content:flex-end" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑产品' : '新增产品'" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类别"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="品牌"><el-input v-model="form.brand" /></el-form-item>
        <el-form-item label="型号"><el-input v-model="form.model" /></el-form-item>
        <el-form-item label="单价(元)"><el-input-number v-model="form.unit_price" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" style="width:100%" /></el-form-item>
        <el-form-item label="起订量"><el-input-number v-model="form.min_order_qty" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="供货周期(天)"><el-input-number v-model="form.lead_time_days" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="规格说明"><el-input v-model="form.specification" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProducts, createProduct, updateProduct } from '../../api'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const dialogVisible = ref(false)
const editingId = ref(null)
const filters = reactive({ keyword: '' })

const form = reactive({ name: '', category: '', brand: '', model: '', unit_price: 0, unit: '个', min_order_qty: 1, lead_time_days: 7, specification: '', remark: '' })

async function loadData() {
  loading.value = true
  try {
    const { data } = await getProducts({ page: page.value, page_size: pageSize, keyword: filters.keyword || undefined })
    const res = data.data
    tableData.value = res?.items || []
    total.value = res?.total || 0
  } finally { loading.value = false }
}

function showDialog(row) {
  if (row) { editingId.value = row.id; Object.assign(form, row) }
  else { editingId.value = null; Object.assign(form, { name: '', category: '', brand: '', model: '', unit_price: 0, unit: '个', min_order_qty: 1, lead_time_days: 7, specification: '', remark: '' }) }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) { await updateProduct(editingId.value, form); ElMessage.success('更新成功') }
  else { await createProduct(form); ElMessage.success('创建成功') }
  dialogVisible.value = false; loadData()
}

onMounted(() => loadData())
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; }
</style>
