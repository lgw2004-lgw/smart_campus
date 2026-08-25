<template>
  <div>
    <div class="page-head"><div><h2>图书馆</h2><p>请选择前往书库或我的借阅</p></div></div>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px">
      <el-card shadow="hover" style="cursor:pointer;border-radius:12px" @click="$router.push('/book-store')">
        <div style="text-align:center;padding:20px 0"><el-icon size="36" color="#1e5eff"><Notebook /></el-icon><h3 style="margin:12px 0 6px">书库</h3><p style="color:#8a94a6;font-size:13px">浏览全部藏书 · 搜索 · 借阅</p><el-button type="primary" round>去书库</el-button></div>
      </el-card>
      <el-card shadow="hover" style="cursor:pointer;border-radius:12px" @click="$router.push('/my-borrow')">
        <div style="text-align:center;padding:20px 0"><el-icon size="36" color="#00b578"><List /></el-icon><h3 style="margin:12px 0 6px">我的借阅</h3><p style="color:#8a94a6;font-size:13px">查看已借阅图书 · 归还 · 罚金</p><el-button type="success" round>去我的借阅</el-button></div>
      </el-card>
    </div>
  </div>
</template>
<script setup lang="ts">
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
</style>
