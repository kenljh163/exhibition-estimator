<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">供应商管理</h1>
      <el-button type="primary" @click="showDialog()"><el-icon><Plus /></el-icon> 新增供应商</el-button>
    </div>

    <div class="filter-bar">
      <el-input v-model="filters.keyword" placeholder="搜索供应商名称" style="width:200px" clearable @clear="loadData" @keyup.enter="loadData" />
      <el-button @click="loadData">搜索</el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="name" label="供应商名称" min-width="180" />
      <el-table-column prop="category" label="供应类别" width="120" />
      <el-table-column prop="city" label="城市" width="80" />
      <el-table-column prop="contact_name" label="联系人" width="90" />
      <el-table-column prop="contact_phone" label="电话" width="120" />
      <el-table-column label="合作等级" width="100">
        <template #default="{ row }">
          <el-tag :type="row.cooperation_level === 'strategic' ? 'danger' : row.cooperation_level === 'preferred' ? 'warning' : 'info'" size="small">
            {{ { strategic: '战略', preferred: '优选', normal: '普通' }[row.cooperation_level] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="评分" width="80">
        <template #default="{ row }">{{ row.rating }}分</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > pageSize"
      layout="total, prev, pager, next"
      :total="total"
      :page-size="pageSize"
      v-model:current-page="page"
      @current-change="loadData"
      style="margin-top:16px;justify-content:flex-end"
    />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑供应商' : '新增供应商'" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="供应类别"><el-input v-model="form.category" placeholder="如：多媒体、展具、灯光" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.contact_phone" /></el-form-item>
        <el-form-item label="城市"><el-input v-model="form.city" /></el-form-item>
        <el-form-item label="合作等级">
          <el-select v-model="form.cooperation_level" style="width:100%">
            <el-option label="战略" value="strategic" />
            <el-option label="优选" value="preferred" />
            <el-option label="普通" value="normal" />
          </el-select>
        </el-form-item>
        <el-form-item label="评分">
          <el-rate v-model="form.rating" :max="5" />
        </el-form-item>
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
import { getSuppliers, createSupplier, updateSupplier } from '../../api'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const dialogVisible = ref(false)
const editingId = ref(null)
const filters = reactive({ keyword: '' })

const form = reactive({ name: '', category: '', contact_name: '', contact_phone: '', city: '', cooperation_level: 'normal', rating: 3, remark: '' })

async function loadData() {
  loading.value = true
  try {
    const { data } = await getSuppliers({ page: page.value, page_size: pageSize, keyword: filters.keyword || undefined })
    const res = data.data
    tableData.value = res?.items || []
    total.value = res?.total || 0
  } finally { loading.value = false }
}

function showDialog(row) {
  if (row) { editingId.value = row.id; Object.assign(form, row) }
  else { editingId.value = null; Object.assign(form, { name: '', category: '', contact_name: '', contact_phone: '', city: '', cooperation_level: 'normal', rating: 3, remark: '' }) }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) { await updateSupplier(editingId.value, form); ElMessage.success('更新成功') }
  else { await createSupplier(form); ElMessage.success('创建成功') }
  dialogVisible.value = false; loadData()
}

onMounted(() => loadData())
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; }
</style>
