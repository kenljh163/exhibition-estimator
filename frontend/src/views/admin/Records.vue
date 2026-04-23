<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">估价记录</h1>
    </div>
    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="created_at" label="时间" width="170" />
      <el-table-column prop="hall_type" label="展厅类型" width="100" />
      <el-table-column prop="area" label="面积(㎡)" width="90" />
      <el-table-column prop="city_level" label="城市等级" width="100" />
      <el-table-column prop="level" label="档次" width="80" />
      <el-table-column prop="schedule_days" label="工期" width="70" />
      <el-table-column label="概算区间" width="220">
        <template #default="{ row }">
          ¥{{ row.total_min?.toLocaleString() }} ~ ¥{{ row.total_max?.toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="单价区间" width="180">
        <template #default="{ row }">
          ¥{{ row.unit_min?.toLocaleString() }} ~ ¥{{ row.unit_max?.toLocaleString() }}/㎡
        </template>
      </el-table-column>
      <el-table-column prop="contact_name" label="联系人" width="80" />
      <el-table-column prop="contact_company" label="公司" width="120" />
      <el-table-column prop="source" label="来源" width="80" />
    </el-table>
    <el-pagination v-if="total > pageSize" layout="total, prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="loadData" style="margin-top:16px;justify-content:flex-end" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getEstimationRecords } from '../../api'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

async function loadData() {
  loading.value = true
  try {
    const { data } = await getEstimationRecords({ page: page.value, page_size: pageSize })
    const res = data.data
    tableData.value = res?.items || []
    total.value = res?.total || 0
  } finally { loading.value = false }
}

onMounted(() => loadData())
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text-primary); }
</style>
