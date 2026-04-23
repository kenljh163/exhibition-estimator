<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">单价参数管理</h1>
      <el-button type="primary" @click="showDialog()">
        <el-icon><Plus /></el-icon> 新增参数
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="hall_type" label="展厅类型" width="120" />
      <el-table-column prop="level" label="档次" width="100" />
      <el-table-column label="装修单价(元/㎡)" width="140">
        <template #default="{ row }">¥{{ row.decoration_unit?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="展陈单价(元/㎡)" width="140">
        <template #default="{ row }">¥{{ row.exhibition_unit?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="灯光音响(元/㎡)" width="140">
        <template #default="{ row }">¥{{ row.light_sound_unit?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="设计费率" width="100">
        <template #default="{ row }">{{ (row.design_rate * 100).toFixed(0) }}%</template>
      </el-table-column>
      <el-table-column label="税管费率" width="100">
        <template #default="{ row }">{{ (row.tax_manage_rate * 100).toFixed(0) }}%</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑单价参数' : '新增单价参数'" width="500px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="展厅类型">
          <el-select v-model="form.hall_type" style="width:100%">
            <el-option v-for="t in hallTypes" :key="t.key" :label="t.name" :value="t.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="档次">
          <el-select v-model="form.level" style="width:100%">
            <el-option v-for="l in levels" :key="l.key" :label="l.name" :value="l.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="装修单价(元/㎡)">
          <el-input-number v-model="form.decoration_unit" :min="0" :step="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="展陈单价(元/㎡)">
          <el-input-number v-model="form.exhibition_unit" :min="0" :step="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="灯光音响(元/㎡)">
          <el-input-number v-model="form.light_sound_unit" :min="0" :step="50" style="width:100%" />
        </el-form-item>
        <el-form-item label="设计费率(%)">
          <el-input-number v-model="form.design_rate" :min="0" :max="1" :step="0.01" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="税管费率(%)">
          <el-input-number v-model="form.tax_manage_rate" :min="0" :max="1" :step="0.01" :precision="2" style="width:100%" />
        </el-form-item>
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
import { getPriceParams, createPriceParam, updatePriceParam, deletePriceParam, getDictionaries } from '../../api'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const hallTypes = ref([])
const levels = ref([])

const form = reactive({
  hall_type: 'enterprise', level: 'standard',
  decoration_unit: 0, exhibition_unit: 0, light_sound_unit: 0,
  design_rate: 0.10, tax_manage_rate: 0.18,
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getPriceParams()
    tableData.value = data.data || []
  } finally { loading.value = false }
}

async function loadDicts() {
  const { data } = await getDictionaries()
  hallTypes.value = data.hall_types
  levels.value = data.levels
}

function showDialog(row) {
  if (row) {
    editingId.value = row.id
    Object.assign(form, row)
  } else {
    editingId.value = null
    Object.assign(form, { hall_type: 'enterprise', level: 'standard', decoration_unit: 0, exhibition_unit: 0, light_sound_unit: 0, design_rate: 0.10, tax_manage_rate: 0.18 })
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) {
    await updatePriceParam(editingId.value, form)
    ElMessage.success('更新成功')
  } else {
    await createPriceParam(form)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadData()
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除该参数？', '提示')
  await deletePriceParam(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => { loadData(); loadDicts() })
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
