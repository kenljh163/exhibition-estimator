<template>
  <div class="estimator-page">
    <!-- 顶部导航 -->
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-icon">◆</span>
          <span class="logo-text">展厅智能概算</span>
        </div>
        <nav class="nav-links">
          <router-link to="/" class="nav-link active">估价工具</router-link>
          <a href="javascript:void(0)" class="nav-link" @click="showHistory = true">历史记录</a>
          <router-link to="/admin" class="nav-link">管理后台</router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="container">
        <!-- 左侧：输入表单 -->
        <div class="form-section" :class="{ 'form-narrow': !!result }">
          <div class="section-card">
            <h2 class="section-title">
              <el-icon><Setting /></el-icon>
              参数设置
            </h2>

            <el-form
              ref="formRef"
              :model="form"
              :rules="rules"
              label-position="top"
              size="large"
              @submit.prevent="handleSubmit"
            >
              <el-form-item label="展厅类型" prop="hall_type">
                <el-select v-model="form.hall_type" placeholder="选择展厅类型" style="width:100%">
                  <el-option
                    v-for="item in dicts.hall_types"
                    :key="item.key"
                    :label="item.name"
                    :value="item.key"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="展厅面积（㎡）" prop="area">
                <el-input-number
                  v-model="form.area"
                  :min="50"
                  :max="50000"
                  :step="50"
                  controls-position="right"
                  style="width:100%"
                  placeholder="输入展厅面积"
                />
              </el-form-item>

              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="所在城市" prop="city_level">
                    <el-select v-model="form.city_level" placeholder="城市等级" style="width:100%">
                      <el-option
                        v-for="item in dicts.city_levels"
                        :key="item.key"
                        :label="item.name"
                        :value="item.key"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="档次定位" prop="level">
                    <el-select v-model="form.level" placeholder="选择档次" style="width:100%">
                      <el-option
                        v-for="item in dicts.levels"
                        :key="item.key"
                        :label="item.name"
                        :value="item.key"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="预计工期">
                <el-select v-model="form.schedule_days" style="width:100%">
                  <el-option
                    v-for="item in dicts.schedule_options"
                    :key="item.days"
                    :label="item.label"
                    :value="item.days"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="附加展项（可选）">
                <div class="exhibit-grid">
                  <el-checkbox-group v-model="form.exhibit_items">
                    <el-checkbox
                      v-for="item in dicts.exhibit_items"
                      :key="item.key"
                      :value="item.key"
                      border
                      class="exhibit-checkbox"
                    >
                      {{ item.name }}
                    </el-checkbox>
                  </el-checkbox-group>
                </div>
              </el-form-item>

              <!-- 联系信息（折叠） -->
              <el-collapse v-model="showContact">
                <el-collapse-item title="留下联系方式获取详细方案" name="contact">
                  <el-row :gutter="16">
                    <el-col :span="8">
                      <el-form-item label="姓名">
                        <el-input v-model="form.contact_name" placeholder="您的姓名" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="电话">
                        <el-input v-model="form.contact_phone" placeholder="联系电话" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="公司">
                        <el-input v-model="form.contact_company" placeholder="公司名称" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-collapse-item>
              </el-collapse>

              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="submit-btn"
                @click="handleSubmit"
              >
                <el-icon v-if="!loading"><TrendCharts /></el-icon>
                {{ loading ? '计算中...' : '开始概算' }}
              </el-button>
            </el-form>
          </div>
        </div>

        <!-- 右侧：结果展示 -->
        <div class="result-section" v-if="result">
          <div class="section-card result-card">
            <h2 class="section-title">
              <el-icon><DataAnalysis /></el-icon>
              概算结果
            </h2>

            <!-- 总价区间 -->
            <div class="total-box">
              <div class="total-label">项目概算总价</div>
              <div class="total-range">
                <span class="total-currency">¥</span>
                <span class="total-min">{{ formatMoney(result.total.min) }}</span>
                <span class="total-separator">~</span>
                <span class="total-max">{{ formatMoney(result.total.max) }}</span>
              </div>
              <div class="total-unit">
                约 ¥{{ formatNumber(result.unit_price.min) }} ~ ¥{{ formatNumber(result.unit_price.max) }}/㎡
              </div>
              <div class="param-tags">
                <el-tag type="info" size="small">{{ result.params.hall_type_name }}</el-tag>
                <el-tag type="info" size="small">{{ result.params.area }}㎡</el-tag>
                <el-tag type="info" size="small">{{ result.params.city_level_name }}</el-tag>
                <el-tag type="info" size="small">{{ result.params.level_name }}</el-tag>
              </div>
            </div>

            <!-- 分项明细 -->
            <div class="detail-section">
              <h3 class="detail-title">分项概算明细</h3>
              <div class="detail-list">
                <div
                  class="detail-item"
                  v-for="(item, index) in result.details"
                  :key="index"
                >
                  <div class="detail-header">
                    <span class="detail-name">{{ item.name }}</span>
                    <span class="detail-percent">{{ item.percent }}%</span>
                  </div>
                  <div class="detail-bar-bg">
                    <div
                      class="detail-bar-fill"
                      :style="{ width: item.percent + '%', background: barColors[index] }"
                    ></div>
                  </div>
                  <div class="detail-range">
                    ¥{{ formatMoney(item.range.min) }} ~ ¥{{ formatMoney(item.range.max) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 展项明细 -->
            <div class="detail-section" v-if="result.exhibit_details && result.exhibit_details.length">
              <h3 class="detail-title">多媒体展项</h3>
              <div class="exhibit-detail-list">
                <div
                  class="exhibit-detail-item"
                  v-for="(item, index) in result.exhibit_details"
                  :key="index"
                >
                  <span class="exhibit-detail-name">{{ item.name }}</span>
                  <span class="exhibit-detail-range">
                    ¥{{ formatMoney(item.range.min) }} ~ ¥{{ formatMoney(item.range.max) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 系数信息 -->
            <div class="coefficient-info">
              <div class="coef-item">
                <span class="coef-label">城市系数</span>
                <span class="coef-value">{{ result.params.city_coefficient }}</span>
              </div>
              <div class="coef-item">
                <span class="coef-label">工期系数</span>
                <span class="coef-value">{{ result.params.schedule_coefficient }}</span>
              </div>
            </div>

            <!-- 品牌信息 -->
            <div class="brand-box">
              <div class="brand-logo">
                <span class="brand-icon">◆</span>
                <a class="brand-name" href="https://trf.333f.com" target="_blank">三川田股份 832545</a>
              </div>
              <p class="brand-desc">深耕数字展厅20年，为政府、企业提供一站式展厅解决方案</p>
              <div class="brand-contact">
                <span>📞 400-888-6363</span>
                <span>🌐 trf.333f.com</span>
              </div>
              <p class="brand-tagline">如需详细方案与精准报价，欢迎联系我们的专业顾问</p>
            </div>

            <!-- 说明 -->
            <div class="disclaimer">
              <el-icon><InfoFilled /></el-icon>
              <p>以上为市场参考价区间，最终报价以实际方案为准。概算有效期30天。</p>
            </div>

            <!-- 预算对比模块 -->
            <div class="budget-compare-section">
              <h3 class="detail-title">
                <el-icon><Coin /></el-icon>
                预算对比分析
              </h3>
              <p class="budget-subtitle">输入客户预算，智能对比分析并给出优化建议</p>
              <div class="budget-input-row">
                <el-input
                  v-model="budgetInputStr"
                  placeholder="请输入客户预算"
                  style="flex:1"
                  size="large"
                  clearable
                >
                  <template #append>万元</template>
                </el-input>
                <el-button
                  type="primary"
                  size="large"
                  :loading="budgetLoading"
                  @click="handleBudgetCompare"
                  style="margin-left:12px"
                >
                  <el-icon v-if="!budgetLoading"><MagicStick /></el-icon>
                  {{ budgetLoading ? '分析中...' : '智能对比' }}
                </el-button>
              </div>

              <!-- 对比结果 -->
              <div class="budget-result" v-if="budgetResult">
                <!-- 可行性评级 -->
                <div class="feasibility-badge" :class="'feasibility-' + budgetResult.feasibility">
                  <span class="feasibility-icon">{{ feasibilityIcons[budgetResult.feasibility] }}</span>
                  <span class="feasibility-text">{{ budgetResult.comparison.feasibility_label }}</span>
                  <span class="feasibility-diff">
                    {{ budgetResult.comparison.diff_ratio > 0 ? '+' : '' }}{{ budgetResult.comparison.diff_ratio }}%
                    （{{ budgetResult.comparison.diff > 0 ? '盈余' : '缺口' }}
                    ¥{{ formatMoney(Math.abs(budgetResult.comparison.diff)) }}）
                  </span>
                </div>

                <!-- 简要匹配提示 -->
                <div class="budget-match-msg" v-if="budgetResult.message">
                  <el-icon><InfoFilled /></el-icon>
                  {{ budgetResult.message }}
                </div>

                <!-- 分项对比条形图 -->
                <div class="compare-chart" v-if="budgetResult.comparison.items">
                  <div class="compare-bar-item" v-for="item in budgetResult.comparison.items" :key="item.name">
                    <div class="compare-bar-label">
                      <span>{{ item.name }}</span>
                      <span class="compare-bar-diff" :class="item.diff >= 0 ? 'positive' : 'negative'">
                        {{ item.diff >= 0 ? '+' : '' }}{{ (item.diff / 10000).toFixed(1) }}万
                      </span>
                    </div>
                    <div class="compare-bar-track">
                      <div
                        class="compare-bar-estimate"
                        :style="{ width: Math.min(100, (item.estimate_avg / (budgetResult.comparison.budget * 0.5)) * 100) + '%' }"
                        title="概算均价"
                      ></div>
                      <div
                        class="compare-bar-budget"
                        :style="{ width: Math.min(100, (item.allocated / (budgetResult.comparison.budget * 0.5)) * 100) + '%' }"
                        title="预算分配"
                      ></div>
                    </div>
                    <div class="compare-bar-legend">
                      <span>概算: ¥{{ (item.estimate_avg / 10000).toFixed(1) }}万</span>
                      <span>分配: ¥{{ (item.allocated / 10000).toFixed(1) }}万</span>
                    </div>
                  </div>
                </div>

                <!-- AI建议 -->
                <div class="ai-advice-section" v-if="budgetResult.advice">
                  <div class="ai-advice-header">
                    <span class="ai-badge">AI 建议</span>
                    <span class="ai-summary">{{ budgetResult.advice.summary }}</span>
                  </div>

                  <div class="advice-list" v-if="budgetResult.advice.suggestions && budgetResult.advice.suggestions.length">
                    <div class="advice-card" v-for="(s, i) in budgetResult.advice.suggestions" :key="i">
                      <div class="advice-card-header">
                        <span class="advice-target">{{ s.target }}</span>
                        <el-tag size="small" :type="s.impact === '低' ? 'success' : s.impact === '中' ? 'warning' : 'danger'">
                          影响: {{ s.impact }}
                        </el-tag>
                      </div>
                      <div class="advice-action">{{ s.action }}</div>
                      <div class="advice-saving" v-if="s.saving_min">
                        可节省 <strong>¥{{ (s.saving_min / 10000).toFixed(1) }}~{{ (s.saving_max / 10000).toFixed(1) }}万</strong>
                      </div>
                      <div class="advice-saving" v-if="s.addition_min">
                        建议增加 <strong>¥{{ (s.addition_min / 10000).toFixed(1) }}~{{ (s.addition_max / 10000).toFixed(1) }}万</strong>
                      </div>
                    </div>
                  </div>

                  <!-- 优化方案 -->
                  <div class="optimized-plan" v-if="budgetResult.advice.optimized_plan && budgetResult.advice.optimized_plan.length">
                    <h4 class="plan-title">优化后预算分配</h4>
                    <div class="plan-table">
                      <div class="plan-row plan-header">
                        <span>分项</span>
                        <span>原始</span>
                        <span>优化后</span>
                        <span>变化</span>
                      </div>
                      <div class="plan-row" v-for="p in budgetResult.advice.optimized_plan" :key="p.name">
                        <span>{{ p.name }}</span>
                        <span>¥{{ (p.original_avg / 10000).toFixed(1) }}万</span>
                        <span>¥{{ (p.optimized / 10000).toFixed(1) }}万</span>
                        <span :class="(p.optimized - p.original_avg) >= 0 ? 'positive' : 'negative'">
                          {{ (p.optimized - p.original_avg) >= 0 ? '+' : '' }}{{ ((p.optimized - p.original_avg) / 10000).toFixed(1) }}万
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 总结建议 -->
                  <div class="overall-advice" v-if="budgetResult.advice.overall_advice">
                    <el-icon><ChatDotRound /></el-icon>
                    {{ budgetResult.advice.overall_advice }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="result-actions">
              <el-button type="primary" size="large" @click="exportPDF">
                <el-icon><Download /></el-icon>
                导出PDF
              </el-button>
              <el-button size="large" @click="shareResult">
                <el-icon><Share /></el-icon>
                分享给客户
              </el-button>
              <el-button size="large" @click="resetForm">
                <el-icon><RefreshLeft /></el-icon>
                重新估价
              </el-button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div class="empty-result" v-if="!result">
          <div class="empty-icon">
            <el-icon :size="64" color="#2a3555"><TrendCharts /></el-icon>
          </div>
          <p class="empty-text">填写左侧参数，点击"开始概算"</p>
          <p class="empty-sub">系统将为您快速生成展厅造价参考报告</p>
        </div>
      </div>
    </main>

    <!-- 分享弹窗 -->
    <el-dialog v-model="showShareDialog" title="分享报价给客户" width="440px" :close-on-click-modal="false">
      <div class="share-dialog-content">
        <div class="share-link-box">
          <label>分享链接</label>
          <div class="share-link-row">
            <input class="share-link-input" :value="shareUrl" readonly ref="shareLinkInput" />
            <el-button type="primary" size="small" @click="copyShareLink">复制</el-button>
          </div>
          <p class="share-tip">复制链接发送给客户，客户打开即可查看报价详情</p>
        </div>

        <el-divider>或者</el-divider>

        <div class="share-poster-box">
          <label>保存海报图片</label>
          <p class="share-tip">保存海报发送到微信/朋友圈，客户扫码查看</p>
          <div class="poster-preview" v-if="posterLoading">
            <el-icon :size="32" class="is-loading"><Loading /></el-icon>
            <span>海报生成中...</span>
          </div>
          <div class="poster-preview" v-else-if="posterUrl">
            <img :src="posterUrl" alt="分享海报" class="poster-img" />
          </div>
          <div class="poster-actions" v-if="posterUrl">
            <el-button type="primary" @click="downloadPoster">
              <el-icon><Download /></el-icon>
              保存图片
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 历史记录抽屉 -->
    <el-drawer v-model="showHistory" title="估价历史记录" size="520px" direction="rtl">
      <div class="history-list" v-if="historyRecords.length">
        <div class="history-item" v-for="record in historyRecords" :key="record.id">
          <div class="history-header">
            <span class="history-type">{{ record.hall_type_name }}</span>
            <span class="history-date">{{ record.created_at }}</span>
          </div>
          <div class="history-info">
            <span>{{ record.area }}㎡ · {{ record.city_level_name }} · {{ record.level_name }}</span>
          </div>
          <div class="history-price">
            ¥{{ formatMoney(record.total_min) }} ~ ¥{{ formatMoney(record.total_max) }}
          </div>
          <div class="history-contact" v-if="record.contact_name">
            <el-tag size="small" type="info">{{ record.contact_name }}</el-tag>
            <span v-if="record.contact_phone" class="history-phone">{{ record.contact_phone }}</span>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无估价记录" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getDictionaries, createEstimation, createShareLink, compareBudget } from '../api'
import axios from 'axios'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)
const showContact = ref([])
const showHistory = ref(false)
const showShareDialog = ref(false)
const shareUrl = ref('')
const shareToken = ref('')
const posterUrl = ref('')
const posterLoading = ref(false)
const historyRecords = ref([])

// 预算对比
const budgetInputStr = ref('')
const budgetLoading = ref(false)
const budgetResult = ref(null)
const feasibilityIcons = {
  sufficient: '🟢',
  adequate: '🔵',
  tight: '🟡',
  insufficient: '🟠',
  severe: '🔴',
}

const form = reactive({
  hall_type: 'enterprise',
  area: 500,
  city_level: 'tier1',
  level: 'standard',
  schedule_days: 60,
  exhibit_items: [],
  contact_name: '',
  contact_phone: '',
  contact_company: '',
})

const rules = {
  hall_type: [{ required: true, message: '请选择展厅类型', trigger: 'change' }],
  area: [{ required: true, message: '请输入展厅面积', trigger: 'blur' }],
  city_level: [{ required: true, message: '请选择城市等级', trigger: 'change' }],
  level: [{ required: true, message: '请选择档次', trigger: 'change' }],
}

const dicts = reactive({
  hall_types: [],
  levels: [],
  city_levels: [],
  schedule_options: [],
  exhibit_items: [],
})

const barColors = [
  'linear-gradient(90deg, #3b82f6, #60a5fa)',
  'linear-gradient(90deg, #06b6d4, #22d3ee)',
  'linear-gradient(90deg, #8b5cf6, #a78bfa)',
  'linear-gradient(90deg, #f59e0b, #fbbf24)',
  'linear-gradient(90deg, #10b981, #34d399)',
]

onMounted(async () => {
  try {
    const { data } = await getDictionaries()
    Object.assign(dicts, data)
  } catch (e) {
    console.error('加载字典失败', e)
  }
})

watch(showHistory, (val) => {
  if (val) loadHistory()
})

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const { data } = await createEstimation({ ...form })
    result.value = data
    loadHistory()
  } catch (e) {
    console.error('概算失败', e)
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  try {
    const { data } = await axios.get('/api/admin/estimation-records', { params: { page_size: 20 } })
    historyRecords.value = data.data?.items || []
  } catch (e) {
    console.error('加载历史记录失败', e)
  }
}

function formatMoney(value) {
  if (!value) return '0'
  return value.toLocaleString('zh-CN')
}

function formatNumber(value) {
  if (!value) return '0'
  return value.toLocaleString('zh-CN')
}

function resetForm() {
  result.value = null
  budgetInputStr.value = ''
  budgetResult.value = null
  form.exhibit_items = []
  form.contact_name = ''
  form.contact_phone = ''
  form.contact_company = ''
}

async function exportPDF() {
  try {
    ElMessage.info('正在生成PDF报告...')
    const response = await axios.post('/api/estimate-pdf', { ...form }, {
      responseType: 'blob',
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `展厅概算报告_${form.hall_type}_${form.area}㎡.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('PDF报告已下载')
  } catch (e) {
    ElMessage.error('PDF生成失败，请重试')
    console.error('PDF导出失败', e)
  }
}

async function shareResult() {
  if (!result.value || !result.value.record_id) {
    ElMessage.warning('请先完成概算')
    return
  }
  try {
    const { data } = await createShareLink(result.value.record_id)
    shareUrl.value = `${window.location.origin}${data.url}`
    shareToken.value = data.url.replace('/share/', '')
    showShareDialog.value = true

    // 自动生成海报
    posterUrl.value = ''
    posterLoading.value = true
    try {
      const resp = await axios.get(`/api/share/${shareToken.value}/poster`, {
        responseType: 'blob',
      })
      posterUrl.value = URL.createObjectURL(resp.data)
    } catch (e) {
      console.error('海报生成失败', e)
    } finally {
      posterLoading.value = false
    }
  } catch (e) {
    ElMessage.error('生成分享链接失败')
    console.error('分享失败', e)
  }
}

async function copyShareLink() {
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('链接已复制')
  } else {
    // fallback
    const input = document.querySelector('.share-link-input')
    if (input) {
      input.select()
      document.execCommand('copy')
      ElMessage.success('链接已复制')
    }
  }
}

function downloadPoster() {
  if (!posterUrl.value) return
  const link = document.createElement('a')
  link.href = posterUrl.value
  link.download = `展厅概算海报_${form.area}㎡.png`
  link.click()
  ElMessage.success('海报已保存')
}

async function handleBudgetCompare() {
  if (!result.value || !result.value.record_id) {
    ElMessage.warning('请先完成概算')
    return
  }
  const budgetWan = parseFloat(budgetInputStr.value)
  if (!budgetWan || budgetWan <= 0) {
    ElMessage.warning('请输入有效的客户预算（万元）')
    return
  }
  budgetLoading.value = true
  budgetResult.value = null
  try {
    // 万元转元
    const budgetYuan = budgetWan * 10000
    console.log('[BudgetCompare] record_id:', result.value.record_id, 'budget:', budgetYuan)
    const resp = await compareBudget(result.value.record_id, budgetYuan)
    console.log('[BudgetCompare] response:', resp)
    budgetResult.value = resp.data
  } catch (e) {
    console.error('预算对比失败', e)
    const msg = e.response?.data?.detail || e.message || '预算对比分析失败'
    ElMessage.error(msg)
  } finally {
    budgetLoading.value = false
  }
}
</script>

<style scoped>
.estimator-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: rgba(17, 24, 39, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  background: var(--gradient-main);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-main);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  transition: all 0.2s;
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-primary);
  background: rgba(59, 130, 246, 0.1);
}

.main-content {
  flex: 1;
  padding: 32px 24px;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.form-section {
  flex: 1;
  min-width: 0;
  transition: flex 0.3s;
}

.form-section.form-narrow {
  flex: 0 0 420px;
}

.result-section {
  flex: 1;
  min-width: 0;
}

.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 28px;
  box-shadow: var(--shadow-card);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
}

.section-title .el-icon {
  color: var(--accent-blue);
}

.exhibit-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.exhibit-checkbox {
  margin-right: 0 !important;
  width: 100%;
}

.exhibit-checkbox :deep(.el-checkbox__label) {
  font-size: 13px;
}

.submit-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
  border-radius: 10px;
  background: var(--gradient-main) !important;
  border: none !important;
  letter-spacing: 2px;
}

/* 结果区域 */
.result-card {
  position: sticky;
  top: 96px;
}

.total-box {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(6, 182, 212, 0.08));
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius);
  padding: 24px;
  text-align: center;
  margin-bottom: 24px;
}

.total-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.total-range {
  font-size: 36px;
  font-weight: 800;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.total-currency {
  font-size: 20px;
  color: var(--accent-cyan);
  font-weight: 600;
}

.total-min,
.total-max {
  background: var(--gradient-main);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.total-separator {
  color: var(--text-muted);
  font-size: 24px;
}

.total-unit {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.param-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.detail-name {
  font-size: 14px;
  color: var(--text-primary);
}

.detail-percent {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
}

.detail-bar-bg {
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.detail-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.detail-range {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: right;
}

.exhibit-detail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.exhibit-detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  font-size: 14px;
}

.exhibit-detail-name {
  color: var(--text-primary);
}

.exhibit-detail-range {
  color: var(--accent-cyan);
  font-weight: 500;
}

.coefficient-info {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.coef-item {
  flex: 1;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  text-align: center;
}

.coef-label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.coef-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-orange);
}

.disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: var(--radius-sm);
  margin-bottom: 20px;
}

.disclaimer .el-icon {
  color: var(--accent-orange);
  margin-top: 1px;
  flex-shrink: 0;
}

.disclaimer p {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.result-actions {
  display: flex;
  gap: 12px;
}

.result-actions .el-button {
  flex: 1;
}

/* 品牌信息 */
.brand-box {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(59, 130, 246, 0.06));
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin-bottom: 20px;
  text-align: center;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 8px;
}

.brand-icon {
  font-size: 22px;
  color: #10b981;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.brand-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.brand-contact {
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 14px;
  color: var(--accent-cyan);
  font-weight: 500;
  margin-bottom: 12px;
}

.brand-tagline {
  font-size: 12px;
  color: var(--text-muted);
}

/* 空状态 */
.empty-result {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
}

.empty-icon {
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-sub {
  font-size: 14px;
  color: var(--text-muted);
}

/* 响应式 */
@media (max-width: 900px) {
  .container {
    flex-direction: column;
  }
  .form-section,
  .form-section.form-narrow {
    flex: none;
    width: 100%;
  }
  .result-card {
    position: static;
  }
  .exhibit-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .header-inner {
    padding: 0 16px;
  }
  .main-content {
    padding: 16px 12px;
  }
  .section-card {
    padding: 20px 16px;
  }
  .total-range {
    font-size: 24px;
  }
  .exhibit-grid {
    grid-template-columns: 1fr;
  }
  .result-actions {
    flex-direction: column;
  }
}

/* 历史记录 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--accent-blue);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.history-type {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.history-date {
  font-size: 12px;
  color: var(--text-muted);
}

.history-info {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.history-price {
  font-size: 16px;
  font-weight: 700;
  color: var(--accent-cyan);
}

.history-contact {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-phone {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 分享弹窗 */
.share-dialog-content {
  text-align: center;
}

.share-link-box {
  text-align: left;
}

.share-link-box label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: block;
  margin-bottom: 8px;
}

.share-link-row {
  display: flex;
  gap: 8px;
}

.share-link-input {
  flex: 1;
  height: 36px;
  padding: 0 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.share-link-input:focus {
  border-color: var(--accent-blue);
}

.share-tip {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

.share-poster-box {
  text-align: center;
}

.share-poster-box label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: block;
  margin-bottom: 8px;
}

.poster-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.poster-img {
  max-width: 100%;
  max-height: 480px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.poster-actions {
  margin-top: 12px;
}

/* 预算对比模块 */
.budget-compare-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.budget-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.budget-input-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.budget-result {
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.feasibility-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: var(--radius);
  margin-bottom: 16px;
}

.feasibility-sufficient { background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); }
.feasibility-adequate { background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.3); }
.feasibility-tight { background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); }
.feasibility-insufficient { background: rgba(249, 115, 22, 0.12); border: 1px solid rgba(249, 115, 22, 0.3); }
.feasibility-severe { background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); }

.feasibility-icon { font-size: 20px; }
.feasibility-text { font-size: 18px; font-weight: 700; }
.feasibility-diff { font-size: 14px; color: var(--text-secondary); margin-left: auto; }

.budget-match-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.08);
  border-radius: var(--radius-sm);
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.budget-match-msg .el-icon { color: var(--accent-blue); }

/* 分项对比条形图 */
.compare-chart {
  margin-bottom: 20px;
}

.compare-bar-item {
  margin-bottom: 14px;
}

.compare-bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.compare-bar-diff.positive { color: #10b981; }
.compare-bar-diff.negative { color: #ef4444; }

.compare-bar-track {
  height: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  position: relative;
}

.compare-bar-estimate {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0.3));
  border-radius: 8px 0 0 8px;
  position: absolute;
  left: 0;
  top: 0;
}

.compare-bar-budget {
  height: 100%;
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.6), rgba(16, 185, 129, 0.4));
  border-radius: 8px;
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0.7;
}

.compare-bar-legend {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* AI建议 */
.ai-advice-section {
  background: rgba(139, 92, 246, 0.06);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: var(--radius);
  padding: 20px;
}

.ai-advice-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.ai-badge {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: white;
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
}

.ai-summary {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.advice-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.advice-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
}

.advice-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.advice-target {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.advice-action {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.advice-saving {
  font-size: 13px;
  color: #10b981;
  margin-top: 6px;
}

.advice-saving strong {
  color: #34d399;
}

/* 优化方案表格 */
.optimized-plan {
  margin-bottom: 16px;
}

.plan-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.plan-table {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.plan-row {
  display: grid;
  grid-template-columns: 2fr 1.2fr 1.2fr 1fr;
  padding: 10px 14px;
  font-size: 13px;
  border-bottom: 1px solid var(--border-color);
}

.plan-row:last-child { border-bottom: none; }

.plan-header {
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-weight: 600;
  font-size: 12px;
}

.plan-row .positive { color: #10b981; }
.plan-row .negative { color: #ef4444; }

.overall-advice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 14px 16px;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.overall-advice .el-icon { color: var(--accent-orange); margin-top: 2px; flex-shrink: 0; }
</style>
