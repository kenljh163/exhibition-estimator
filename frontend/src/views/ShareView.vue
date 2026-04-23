<template>
  <div class="share-page">
    <!-- 顶部 -->
    <header class="share-header">
      <div class="share-header-inner">
        <div class="share-logo">
          <span class="share-logo-icon">◆</span>
          <span class="share-logo-text">展厅智能概算</span>
        </div>
        <span class="share-badge">三川田数字科技</span>
      </div>
    </header>

    <!-- 加载状态 -->
    <div class="share-loading" v-if="loading">
      <el-icon :size="40" class="loading-icon"><Loading /></el-icon>
      <p>加载概算数据...</p>
    </div>

    <!-- 错误状态 -->
    <div class="share-error" v-else-if="error">
      <el-icon :size="64" color="#ef4444"><CircleCloseFilled /></el-icon>
      <h2>{{ errorTitle }}</h2>
      <p>{{ error }}</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>

    <!-- 概算结果 -->
    <main class="share-main" v-else-if="data">
      <div class="share-container">
        <!-- 概算卡片 -->
        <div class="share-card">
          <h1 class="share-title">展厅概算报告</h1>
          <p class="share-date">生成时间：{{ data.created_at }}</p>

          <!-- 项目参数 -->
          <div class="share-params">
            <div class="param-chip">
              <span class="param-label">展厅类型</span>
              <span class="param-value">{{ data.hall_type_name }}</span>
            </div>
            <div class="param-chip">
              <span class="param-label">面积</span>
              <span class="param-value">{{ data.area }}㎡</span>
            </div>
            <div class="param-chip">
              <span class="param-label">城市等级</span>
              <span class="param-value">{{ data.city_level_name }}</span>
            </div>
            <div class="param-chip">
              <span class="param-label">档次定位</span>
              <span class="param-value">{{ data.level_name }}</span>
            </div>
            <div class="param-chip">
              <span class="param-label">预计工期</span>
              <span class="param-value">{{ data.schedule_days }}天</span>
            </div>
          </div>

          <!-- 总价 -->
          <div class="share-total-box">
            <div class="share-total-label">项目概算总价区间</div>
            <div class="share-total-range">
              <span class="share-currency">¥</span>
              <span class="share-total-min">{{ formatMoney(data.total_min) }}</span>
              <span class="share-sep">~</span>
              <span class="share-total-max">{{ formatMoney(data.total_max) }}</span>
            </div>
            <div class="share-unit-range">
              约 ¥{{ formatMoney(data.unit_min) }} ~ ¥{{ formatMoney(data.unit_max) }}/㎡
            </div>
          </div>

          <!-- 分项明细 -->
          <div class="share-detail-section" v-if="data.details && data.details.length">
            <h3 class="share-detail-title">分项概算明细</h3>
            <div class="share-detail-list">
              <div class="share-detail-item" v-for="(item, index) in data.details" :key="index">
                <div class="share-detail-header">
                  <span class="share-detail-name">{{ item.name }}</span>
                  <span class="share-detail-percent">{{ item.percent }}%</span>
                </div>
                <div class="share-detail-bar">
                  <div class="share-detail-fill" :style="{ width: item.percent + '%', background: barColors[index % barColors.length] }"></div>
                </div>
                <div class="share-detail-price">
                  ¥{{ formatMoney(item.range.min) }} ~ ¥{{ formatMoney(item.range.max) }}
                </div>
              </div>
            </div>
          </div>

          <!-- 展项 -->
          <div class="share-exhibit-section" v-if="data.exhibit_details && data.exhibit_details.length">
            <h3 class="share-detail-title">多媒体展项</h3>
            <div class="share-exhibit-list">
              <div class="share-exhibit-item" v-for="(item, index) in data.exhibit_details" :key="index">
                <span class="share-exhibit-name">{{ item.name }}</span>
                <span class="share-exhibit-price">¥{{ formatMoney(item.range.min) }} ~ ¥{{ formatMoney(item.range.max) }}</span>
              </div>
            </div>
          </div>

          <!-- 品牌信息 -->
          <div class="share-brand">
            <div class="share-brand-logo">
              <span class="share-brand-icon">◆</span>
              <span class="share-brand-name">{{ data.brand.company }}</span>
            </div>
            <p class="share-brand-desc">{{ data.brand.desc }}</p>
            <div class="share-brand-contacts">
              <span>📞 {{ data.brand.phone }}</span>
              <span>🌐 {{ data.brand.website }}</span>
            </div>
          </div>

          <!-- 免责 -->
          <div class="share-disclaimer">
            <p>以上为市场参考价区间，最终报价以实际方案为准。概算有效期30天。</p>
          </div>
        </div>

        <!-- 留资卡片 -->
        <div class="lead-card" v-if="!leadSubmitted">
          <h2 class="lead-title">
            <el-icon><UserFilled /></el-icon>
            获取详细方案与精准报价
          </h2>
          <p class="lead-desc">留下您的联系方式，我们的专业顾问将在24小时内与您联系</p>
          <el-form
            ref="leadFormRef"
            :model="leadForm"
            :rules="leadRules"
            label-position="top"
            size="large"
          >
            <el-form-item label="姓名" prop="name">
              <el-input v-model="leadForm.name" placeholder="请输入您的姓名" />
            </el-form-item>
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="leadForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="公司名称">
              <el-input v-model="leadForm.company" placeholder="选填" />
            </el-form-item>
            <el-form-item label="需求说明">
              <el-input v-model="leadForm.remark" type="textarea" :rows="3" placeholder="选填，如展厅用途、特殊要求等" />
            </el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="leadLoading"
              class="lead-submit-btn"
              @click="handleLeadSubmit"
            >
              提交并获取方案
            </el-button>
          </el-form>
        </div>

        <!-- 留资成功 -->
        <div class="lead-success-card" v-else>
          <el-icon :size="56" color="#10b981"><CircleCheckFilled /></el-icon>
          <h3>提交成功！</h3>
          <p>我们的专业顾问将在24小时内与您联系</p>
          <p class="lead-success-phone">咨询热线：{{ data.brand.phone }}</p>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="share-footer">
      <p>© {{ new Date().getFullYear() }} {{ data?.brand?.company || '三川田数字科技' }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getShareData, submitLead } from '../api'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const errorTitle = ref('无法加载')
const data = ref(null)
const leadSubmitted = ref(false)
const leadLoading = ref(false)
const leadFormRef = ref(null)

const leadForm = reactive({
  name: '',
  phone: '',
  company: '',
  remark: '',
})

const leadRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
}

const barColors = [
  'linear-gradient(90deg, #3b82f6, #60a5fa)',
  'linear-gradient(90deg, #06b6d4, #22d3ee)',
  'linear-gradient(90deg, #8b5cf6, #a78bfa)',
  'linear-gradient(90deg, #f59e0b, #fbbf24)',
  'linear-gradient(90deg, #10b981, #34d399)',
]

onMounted(async () => {
  const token = route.params.token
  if (!token) {
    error.value = '缺少分享参数'
    loading.value = false
    return
  }
  try {
    const { data: resp } = await getShareData(token)
    data.value = resp
  } catch (e) {
    if (e.response?.status === 410) {
      errorTitle.value = '链接已过期'
      error.value = '该分享链接已超过有效期，请联系我们获取最新方案'
    } else if (e.response?.status === 404) {
      errorTitle.value = '链接不存在'
      error.value = '该分享链接无效或已被禁用'
    } else {
      error.value = '加载失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
})

function formatMoney(value) {
  if (!value) return '0'
  return value.toLocaleString('zh-CN')
}

async function handleLeadSubmit() {
  const valid = await leadFormRef.value?.validate().catch(() => false)
  if (!valid) return

  leadLoading.value = true
  try {
    const token = route.params.token
    await submitLead(token, { ...leadForm })
    leadSubmitted.value = true
    ElMessage.success('提交成功！')
  } catch (e) {
    ElMessage.error('提交失败，请重试')
  } finally {
    leadLoading.value = false
  }
}
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #0f172a);
}

.share-header {
  background: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color, rgba(255,255,255,0.08));
  position: sticky;
  top: 0;
  z-index: 100;
}

.share-header-inner {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.share-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.share-logo-icon {
  font-size: 22px;
  background: var(--gradient-main, linear-gradient(135deg, #3b82f6, #06b6d4));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.share-logo-text {
  font-size: 18px;
  font-weight: 700;
  background: var(--gradient-main, linear-gradient(135deg, #3b82f6, #06b6d4));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.share-badge {
  font-size: 13px;
  color: var(--text-secondary, #94a3b8);
  background: rgba(59, 130, 246, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
}

/* Loading & Error */
.share-loading,
.share-error {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--text-secondary, #94a3b8);
}

.share-error h2 {
  color: var(--text-primary, #e2e8f0);
}

/* Main */
.share-main {
  flex: 1;
  padding: 32px 16px;
}

.share-container {
  max-width: 800px;
  margin: 0 auto;
}

/* 概算卡片 */
.share-card {
  background: var(--bg-card, #1e293b);
  border: 1px solid var(--border-color, rgba(255,255,255,0.08));
  border-radius: 16px;
  padding: 32px 28px;
  margin-bottom: 24px;
}

.share-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #e2e8f0);
  text-align: center;
  margin-bottom: 4px;
}

.share-date {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted, #64748b);
  margin-bottom: 24px;
}

.share-params {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-bottom: 24px;
}

.param-chip {
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.15);
  border-radius: 8px;
  padding: 8px 14px;
  text-align: center;
}

.param-label {
  display: block;
  font-size: 11px;
  color: var(--text-muted, #64748b);
  margin-bottom: 2px;
}

.param-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #e2e8f0);
}

.share-total-box {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(6, 182, 212, 0.08));
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  padding: 28px;
  text-align: center;
  margin-bottom: 24px;
}

.share-total-label {
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
  margin-bottom: 10px;
}

.share-total-range {
  font-size: 34px;
  font-weight: 800;
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.share-currency {
  font-size: 20px;
  color: #06b6d4;
  font-weight: 600;
}

.share-total-min,
.share-total-max {
  background: var(--gradient-main, linear-gradient(135deg, #3b82f6, #06b6d4));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.share-sep {
  color: var(--text-muted, #64748b);
  font-size: 22px;
}

.share-unit-range {
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
  margin-top: 8px;
}

/* 分项明细 */
.share-detail-section {
  margin-bottom: 24px;
}

.share-detail-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #e2e8f0);
  margin-bottom: 14px;
}

.share-detail-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.share-detail-item {
  padding: 12px 16px;
  background: var(--bg-secondary, #0f172a);
  border-radius: 10px;
}

.share-detail-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.share-detail-name {
  font-size: 14px;
  color: var(--text-primary, #e2e8f0);
}

.share-detail-percent {
  font-size: 13px;
  color: var(--text-secondary, #94a3b8);
  font-weight: 600;
}

.share-detail-bar {
  height: 5px;
  background: rgba(255,255,255,0.04);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.share-detail-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.share-detail-price {
  font-size: 13px;
  color: var(--text-secondary, #94a3b8);
  text-align: right;
}

/* 展项 */
.share-exhibit-section {
  margin-bottom: 24px;
}

.share-exhibit-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.share-exhibit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--bg-secondary, #0f172a);
  border-radius: 10px;
}

.share-exhibit-name {
  font-size: 14px;
  color: var(--text-primary, #e2e8f0);
}

.share-exhibit-price {
  font-size: 14px;
  color: #06b6d4;
  font-weight: 500;
}

/* 品牌 */
.share-brand {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), rgba(59, 130, 246, 0.04));
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 12px;
  padding: 20px 24px;
  text-align: center;
  margin-bottom: 16px;
}

.share-brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 8px;
}

.share-brand-icon {
  font-size: 20px;
  color: #10b981;
}

.share-brand-name {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary, #e2e8f0);
}

.share-brand-desc {
  font-size: 13px;
  color: var(--text-secondary, #94a3b8);
  margin-bottom: 12px;
}

.share-brand-contacts {
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 14px;
  color: #06b6d4;
  font-weight: 500;
}

.share-disclaimer {
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-radius: 8px;
}

.share-disclaimer p {
  font-size: 12px;
  color: var(--text-muted, #64748b);
  text-align: center;
}

/* 留资卡片 */
.lead-card {
  background: var(--bg-card, #1e293b);
  border: 1px solid var(--border-color, rgba(255,255,255,0.08));
  border-radius: 16px;
  padding: 32px 28px;
  margin-bottom: 24px;
}

.lead-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary, #e2e8f0);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.lead-desc {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
  margin-bottom: 24px;
}

.lead-submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  background: var(--gradient-main, linear-gradient(135deg, #3b82f6, #06b6d4)) !important;
  border: none !important;
  letter-spacing: 1px;
}

/* 留资成功 */
.lead-success-card {
  background: var(--bg-card, #1e293b);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 16px;
  padding: 48px 28px;
  text-align: center;
  margin-bottom: 24px;
}

.lead-success-card h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary, #e2e8f0);
  margin-top: 12px;
  margin-bottom: 8px;
}

.lead-success-card p {
  font-size: 14px;
  color: var(--text-secondary, #94a3b8);
}

.lead-success-phone {
  margin-top: 16px;
  font-size: 16px;
  color: #06b6d4;
  font-weight: 600;
}

/* 底部 */
.share-footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: var(--text-muted, #64748b);
}

/* 响应式 */
@media (max-width: 600px) {
  .share-card,
  .lead-card,
  .lead-success-card {
    padding: 24px 18px;
  }
  .share-total-range {
    font-size: 24px;
  }
  .share-params {
    gap: 8px;
  }
  .param-chip {
    padding: 6px 10px;
  }
}
</style>
