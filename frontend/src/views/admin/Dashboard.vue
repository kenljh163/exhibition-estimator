<template>
  <div class="dashboard">
    <h1 class="page-title">数据概览</h1>
    <div class="stat-grid" v-loading="loading">
      <div class="stat-card" v-for="item in statCards" :key="item.label">
        <div class="stat-icon" :style="{ background: item.bg }">
          <el-icon :size="24" :color="item.color"><component :is="item.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- 按展厅类型统计 -->
    <div class="chart-section" v-if="stats.by_hall_type && stats.by_hall_type.length">
      <h2 class="section-title">按展厅类型统计</h2>
      <el-table :data="stats.by_hall_type" stripe>
        <el-table-column prop="type" label="展厅类型" width="120" />
        <el-table-column prop="count" label="估价次数" width="100" />
        <el-table-column label="平均概算区间">
          <template #default="{ row }">
            ¥{{ (row.avg_min / 10000).toFixed(1) }}万 ~ ¥{{ (row.avg_max / 10000).toFixed(1) }}万
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getStatistics } from '../../api'

const loading = ref(true)
const stats = reactive({
  total_estimations: 0,
  total_contacts: 0,
  total_suppliers: 0,
  total_products: 0,
  by_hall_type: [],
})

const statCards = computed(() => [
  { label: '总估价次数', value: stats.total_estimations, icon: 'TrendCharts', color: '#3b82f6', bg: 'rgba(59,130,246,0.12)' },
  { label: '客户留资数', value: stats.total_contacts, icon: 'User', color: '#10b981', bg: 'rgba(16,185,129,0.12)' },
  { label: '供应商数量', value: stats.total_suppliers, icon: 'OfficeBuilding', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
  { label: '产品数量', value: stats.total_products, icon: 'Box', color: '#8b5cf6', bg: 'rgba(139,92,246,0.12)' },
])

import { computed } from 'vue'

onMounted(async () => {
  try {
    const { data } = await getStatistics()
    Object.assign(stats, data)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--text-primary);
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.chart-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}
</style>
