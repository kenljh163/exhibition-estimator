<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="logo-icon">◆</span>
        <span class="logo-text">管理后台</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin" class="nav-item" :class="{ active: $route.name === 'AdminDashboard' }">
          <el-icon><DataBoard /></el-icon> 数据概览
        </router-link>
        <router-link to="/admin/price-params" class="nav-item" :class="{ active: $route.name === 'AdminPriceParams' }">
          <el-icon><Coin /></el-icon> 单价参数
        </router-link>
        <router-link to="/admin/exhibit-items" class="nav-item" :class="{ active: $route.name === 'AdminExhibitItems' }">
          <el-icon><Grid /></el-icon> 展项管理
        </router-link>
        <router-link to="/admin/suppliers" class="nav-item" :class="{ active: $route.name === 'AdminSuppliers' }">
          <el-icon><OfficeBuilding /></el-icon> 供应商
        </router-link>
        <router-link to="/admin/products" class="nav-item" :class="{ active: $route.name === 'AdminProducts' }">
          <el-icon><Box /></el-icon> 产品库
        </router-link>
        <router-link to="/admin/quotes" class="nav-item" :class="{ active: $route.name === 'AdminQuotes' }">
          <el-icon><Document /></el-icon> 供应商报价
        </router-link>
        <router-link to="/admin/records" class="nav-item" :class="{ active: $route.name === 'AdminRecords' }">
          <el-icon><List /></el-icon> 估价记录
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <router-link to="/" class="nav-item">
          <el-icon><Back /></el-icon> 返回前台
        </router-link>
      </div>
    </aside>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px 20px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--border-color);
}

.logo-icon {
  font-size: 20px;
  background: var(--gradient-main);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.08);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-blue-light);
  font-weight: 500;
}

.sidebar-footer {
  padding: 8px;
  border-top: 1px solid var(--border-color);
}

.admin-main {
  flex: 1;
  padding: 24px;
  min-width: 0;
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
    flex-direction: row;
    overflow-x: auto;
  }
  .sidebar-header {
    display: none;
  }
  .sidebar-nav {
    flex-direction: row;
    padding: 8px;
    gap: 4px;
  }
  .sidebar-footer {
    border-top: none;
    border-left: 1px solid var(--border-color);
  }
  .nav-item {
    white-space: nowrap;
    font-size: 12px;
    padding: 8px 10px;
  }
}
</style>
