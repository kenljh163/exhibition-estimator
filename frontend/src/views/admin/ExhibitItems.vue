<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">展项管理</h1>
      <el-button type="primary" @click="showDialog()"><el-icon><Plus /></el-icon> 新增展项</el-button>
    </div>
    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="item_name" label="展项名称" width="160" />
      <el-table-column prop="item_key" label="标识Key" width="160" />
      <el-table-column prop="level" label="档次" width="100" />
      <el-table-column label="参考价(万元)" width="200">
        <template #default="{ row }">{{ row.price_min }} ~ {{ row.price_max }}</template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="60" />
      <el-table-column prop="sort_order" label="排序" width="70" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑展项' : '新增展项'" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="展项名称"><el-input v-model="form.item_name" /></el-form-item>
        <el-form-item label="标识Key"><el-input v-model="form.item_key" :disabled="!!editingId" /></el-form-item>
        <el-form-item label="档次">
          <el-select v-model="form.level" style="width:100%">
            <el-option v-for="l in levels" :key="l.key" :label="l.name" :value="l.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="最低价(万元)"><el-input-number v-model="form.price_min" :min="0" :step="1" style="width:100%" /></el-form-item>
        <el-form-item label="最高价(万元)"><el-input-number v-model="form.price_max" :min="0" :step="1" style="width:100%" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" style="width:100%" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
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
import { getExhibitItems, createExhibitItem, updateExhibitItem, deleteExhibitItem, getDictionaries } from '../../api'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const levels = ref([])

const form = reactive({ item_name: '', item_key: '', level: 'standard', price_min: 0, price_max: 0, unit: '项', sort_order: 0, description: '' })

async function loadData() {
  loading.value = true
  try { const { data } = await getExhibitItems(); tableData.value = data.data || [] }
  finally { loading.value = false }
}

async function loadDicts() {
  const { data } = await getDictionaries()
  levels.value = data.levels
}

function showDialog(row) {
  if (row) { editingId.value = row.id; Object.assign(form, row) }
  else { editingId.value = null; Object.assign(form, { item_name: '', item_key: '', level: 'standard', price_min: 0, price_max: 0, unit: '项', sort_order: 0, description: '' }) }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) { await updateExhibitItem(editingId.value, form); ElMessage.success('更新成功') }
  else { await createExhibitItem(form); ElMessage.success('创建成功') }
  dialogVisible.value = false; loadData()
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除？', '提示')
  await deleteExhibitItem(id); ElMessage.success('删除成功'); loadData()
}

onMounted(() => { loadData(); loadDicts() })
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); }
</style>
