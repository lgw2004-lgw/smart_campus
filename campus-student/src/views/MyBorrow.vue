<template>
  <div>
    <div class="page-head"><el-button @click="router.push('/my-book')">返回图书馆</el-button></div>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:700">我的借阅</span><el-tag type="info">{{ myBorrows.length }} 本</el-tag></div></template>
      <div v-for="r in myBorrows" :key="r.borrow_id" class="borrow-row">
        <div><div style="font-weight:600">{{ bookMap[r.book_id] || r.book_id }}</div><div style="font-size:12px;color:#8a94a6">应还 {{ r.due_time?.slice(0,10) }} · 罚金 ¥{{ r.fine }}</div></div>
        <div style="display:flex;align-items:center;gap:8px"><el-tag :type="r.status==='0'?'warning':'success'" effect="plain">{{ r.status==='0'?'借出':'已还' }}</el-tag><el-button size="small" :disabled="r.status==='1'" @click="ret(r)">归还</el-button></div>
      </div>
      <el-empty v-if="!myBorrows.length" description="暂无借阅" />
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const router=useRouter()
const sid=localStorage.getItem('studentId')||''
const myBorrows=ref<any[]>([])
const bookMap=ref<Record<string,string>>({})
async function loadBooksMap(){
  const res:any=await request.post('/book/queryByPage', {pageNo:1,pageSize:2000,data:{}})
  const m:Record<string,string>={}
  for(const b of (res.data.list||[])) m[b.book_id]=b.book_name
  bookMap.value=m
}
async function loadMine(){ const res:any=await request.post('/borrow/queryByPage', {pageNo:1,pageSize:20,data:{studentId:sid}}); myBorrows.value=res.data.list||[] }
async function ret(row:any){ const res:any=await request.post(`/borrow/return/${row.borrow_id}`); ElMessage.success(`已归还 罚金 ${res.data.fine}`); loadMine() }
onMounted(async()=>{ await loadBooksMap(); await loadMine() })
</script>
<style scoped>
.borrow-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f0f2f5}
.borrow-row:last-child{border-bottom:none}
.page-head{display:flex;align-items:center;margin-bottom:12px}
</style>
