<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">供应商报价</h1>
      <el-button type="primary" @click="showDialog()"><el-icon><Plus /></el-icon> 新增报价</el-button>
    </div>
    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="category" label="类别" width="100" />
      <el-table-column prop="item_name" label="报价项目" min-width="160" />
      <el-table-column label="单价(元)" width="100">
        <template #default="{ row }">¥{{ row.unit_price?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="70" />
      <el-table-column label="总价(元)" width="120">
        <template #default="{ row }">¥{{ row.total_price?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column prop="project_type" label="适用项目" width="100" />
      <el-table-column prop="created_at" label="日期" width="170" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > pageSize" layout="total, prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="loadData" style="margin-top:16px;justify-content:flex-end" />

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑报价' : '新增报价'" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="供应商ID"><el-input-number v-model="form.supplier_id" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="类别"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="项目名称"><el-input v-model="form.item_name" /></el-form-item>
        <el-form-item label="规格要求"><el-input v-model="form.specification" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="单价(元)"><el-input-number v-model="form.unit_price" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="有效期"><el-input v-model="form.valid_until" placeholder="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="适用项目"><el-input v-model="form.project_type" /></el-form-item>
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
import { getSupplierQuotes, createSupplierQuote, updateSupplierQuote } from '../../api'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const dialogVisible = ref(false)
const editingId = ref(null)

const form = reactive({ supplier_id: 1, category: '', item_name: '', specification: '', unit_price: 0, quantity: 1, total_price: 0, valid_until: '', project_type: '', remark: '' })

async function loadData() {
  loading.value = true
  try {
    const { data } = await getSupplierQuotes({ page: page.value, page_size: pageSize })
    const res = data.data
    tableData.value = res?.items || []
    total.value = res?.total || 0
  } finally { loading.value = false }
}

function showDialog(row) {
  if (row) { editingId.value = row.id; Object.assign(form, row) }
  else { editingId.value = null; Object.assign(form, { supplier_id: 1, category: '', item_name: '', specification: '', unit_price: 0, quantity: 1, total_price: 0, valid_until: '', project_type: '', remark: '' }) }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) { await updateSupplierQuote(editingId.value, form); ElMessage.success('更新成功') }
  else { await createSupplierQuote(form); ElMessage.success('创建成功') }
  dialogVisible.value = false; loadData()
}

onMounted(() => loadData())
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); }
</style>
