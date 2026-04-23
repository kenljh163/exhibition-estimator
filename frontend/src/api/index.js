import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 获取字典数据
export const getDictionaries = () => api.get('/api/dictionaries')

// 执行概算
export const createEstimation = (data) => api.post('/api/estimate', data)

// ===== 管理后台 =====

// 单价参数
export const getPriceParams = (params) => api.get('/api/admin/price-params', { params })
export const createPriceParam = (data) => api.post('/api/admin/price-params', data)
export const updatePriceParam = (id, data) => api.put(`/api/admin/price-params/${id}`, data)
export const deletePriceParam = (id) => api.delete(`/api/admin/price-params/${id}`)

// 展项管理
export const getExhibitItems = (params) => api.get('/api/admin/exhibit-items', { params })
export const createExhibitItem = (data) => api.post('/api/admin/exhibit-items', data)
export const updateExhibitItem = (id, data) => api.put(`/api/admin/exhibit-items/${id}`, data)
export const deleteExhibitItem = (id) => api.delete(`/api/admin/exhibit-items/${id}`)

// 供应商管理
export const getSuppliers = (params) => api.get('/api/admin/suppliers', { params })
export const createSupplier = (data) => api.post('/api/admin/suppliers', data)
export const updateSupplier = (id, data) => api.put(`/api/admin/suppliers/${id}`, data)
export const getSupplierDetail = (id) => api.get(`/api/admin/suppliers/${id}`)

// 产品库
export const getProducts = (params) => api.get('/api/admin/products', { params })
export const createProduct = (data) => api.post('/api/admin/products', data)
export const updateProduct = (id, data) => api.put(`/api/admin/products/${id}`, data)

// 供应商报价
export const getSupplierQuotes = (params) => api.get('/api/admin/supplier-quotes', { params })
export const createSupplierQuote = (data) => api.post('/api/admin/supplier-quotes', data)
export const updateSupplierQuote = (id, data) => api.put(`/api/admin/supplier-quotes/${id}`, data)

// 估价记录
export const getEstimationRecords = (params) => api.get('/api/admin/estimation-records', { params })

// 统计
export const getStatistics = () => api.get('/api/admin/statistics')

// 分享链接
export const createShareLink = (record_id) => api.post('/api/share/create', { record_id })
export const getShareData = (token) => api.get(`/api/share/${token}`)
export const submitLead = (token, data) => api.post(`/api/share/${token}/lead`, data)

// 管理后台 - 分享链接 & 留资
export const getShareLinks = (params) => api.get('/api/admin/share-links', { params })
export const disableShareLink = (id) => api.delete(`/api/admin/share-links/${id}`)
export const getLeads = (params) => api.get('/api/admin/leads', { params })

// 预算对比 & AI建议
export const compareBudget = (record_id, budget) => api.post('/api/budget-compare', { record_id, budget })

export default api
