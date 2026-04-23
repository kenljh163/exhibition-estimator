# 展厅智能概算系统 (Exhibition Smart Estimator)

> A阶段 MVP - 智能估价器

## 快速启动

### 后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
# API: http://localhost:8000
# Swagger文档: http://localhost:8000/docs
```

### 前端
```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

## 技术栈
- **前端**: Vue3 + Vite + Element Plus (深色主题)
- **后端**: Python FastAPI + SQLAlchemy
- **数据库**: SQLite (开发) / PostgreSQL (生产)

## 核心功能

### 前台 - 估价工具
- 展厅参数输入（类型/面积/城市/档次/工期/附加展项）
- 实时概算计算
- 分项明细可视化
- 联系方式留资

### 后台 - 管理系统
- 单价参数维护
- 附加展项管理
- 供应商管理（含合作等级/评分）
- 产品库管理（关联供应商）
- 供应商报价管理
- 估价记录查看
- 数据统计概览

## API 文档
启动后端后访问 http://localhost:8000/docs 查看交互式API文档。

## 数据接口（对接三川田供应链）

系统预留了供应商、产品库、供应商报价三大模块：

| 模块 | 用途 | 对接方向 |
|------|------|---------|
| **供应商** | 管理三川田合作供应商信息 | 对接三川田ERP/CRM |
| **产品库** | 管理展厅相关产品/材料 | 对接供应商产品目录 |
| **供应商报价** | 管理供应商最新报价 | 对接采购系统 |

后续可通过以下方式对接：
1. **API导入**: 通过管理后台或API批量导入
2. **Excel导入**: 支持Excel批量导入供应商和产品
3. **系统对接**: 提供标准REST API，支持与三川田内部系统对接

## 目录结构
```
exhibition-estimator/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── app/
│   │   ├── api/
│   │   │   ├── estimation.py  # 概算API
│   │   │   └── admin.py       # 管理后台API
│   │   ├── models/
│   │   │   └── models.py      # 数据模型
│   │   ├── schemas/
│   │   │   └── schemas.py     # 请求/响应模型
│   │   ├── services/
│   │   │   ├── estimation.py  # 概算引擎
│   │   │   └── seed_data.py   # 种子数据
│   │   └── core/
│   │       └── database.py    # 数据库配置
│   └── .env                  # 环境配置
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── EstimatorView.vue  # 估价主页
│   │   │   └── admin/             # 管理后台
│   │   ├── api/index.js           # API封装
│   │   ├── router/index.js        # 路由
│   │   └── assets/styles/global.css  # 深色主题
│   └── vite.config.js
```

## 当前状态
- [x] 项目框架搭建
- [x] 概算引擎核心逻辑
- [x] 前端估价表单 + 结果展示
- [x] 附加展项估价模块
- [x] 管理后台（完整CRUD）
- [x] 供应商/产品库/报价（数据接口预留）
- [ ] PDF报告导出
- [ ] 生产环境部署
