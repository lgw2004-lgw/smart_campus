<template>
  <div>
    <div class="page-head"><div><h2>图书馆</h2><p>与管理端库存联动 · 借阅30天 逾期 0.5元/天</p></div><el-input v-model="kw" placeholder="搜索书名" prefix-icon="Search" style="width:260px" clearable /></div>
    <div class="book-grid">
      <div class="book-card" v-for="b in filtered" :key="b.book_id">
        <div class="book-cover">{{ b.book_name.slice(0,1) }}</div>
        <div style="flex:1"><div class="book-name">{{ b.book_name }}</div><div class="book-meta">{{ b.author }} · {{ b.category }} · ISBN {{ b.isbn }}</div><div style="margin-top:6px"><el-tag :type="b.stock>0?'success':'danger'" size="small" effect="plain">{{ b.stock }}/{{ b.total }} 可借</el-tag></div></div>
        <el-button type="primary" size="small" round :disabled="b.stock<=0" @click="borrow(b)">借阅</el-button>
      </div>
    </div>
    <el-card shadow="never" style="border-radius:14px;margin-top:16px">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:700">我的借阅</span><el-tag type="info">{{ myBorrows.length }} 本</el-tag></div></template>
      <div v-for="r in myBorrows" :key="r.borrow_id" class="borrow-row">
        <div><div style="font-weight:600">{{ r.book_id }} · {{ r.borrow_id.slice(0,8) }}</div><div style="font-size:12px;color:#8a94a6">应还 {{ r.due_time?.slice(0,10) }} · 罚金 ¥{{ r.fine }}</div></div>
        <div style="display:flex;align-items:center;gap:8px"><el-tag :type="r.status==='0'?'warning':'success'" effect="plain">{{ r.status==='0'?'借出':'已还' }}</el-tag><el-button size="small" :disabled="r.status==='1'" @click="ret(r)">归还</el-button></div>
      </div>
      <el-empty v-if="!myBorrows.length" description="暂无借阅" />
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const books=ref<any[]>([]); const kw=ref('')
async function loadBooks(){ const res:any=await request.post('/book/queryByPage', {pageNo:1,pageSize:30,data:{}}); books.value=res.data.list||[] }
const filtered=computed(()=> kw.value? books.value.filter((b:any)=>b.book_name.includes(kw.value)): books.value)
async function borrow(row:any){ await request.post('/borrow/add', {studentId:sid, bookId:row.book_id}); ElMessage.success('借阅成功'); loadBooks(); loadMine() }
const myBorrows=ref<any[]>([])
async function loadMine(){ const res:any=await request.post('/borrow/queryByPage', {pageNo:1,pageSize:20,data:{studentId:sid}}); myBorrows.value=res.data.list||[] }
async function ret(row:any){ const res:any=await request.post(`/borrow/return/${row.borrow_id}`); ElMessage.success(`已归还 罚金 ${res.data.fine}`); loadMine(); loadBooks() }
onMounted(()=>{ loadBooks(); loadMine() })
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.book-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.book-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px;display:flex;gap:12px;align-items:center}
.book-cover{width:44px;height:56px;background:linear-gradient(135deg,#1e5eff,#5b8cff);color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px}
.book-name{font-weight:700}
.book-meta{font-size:12px;color:#8a94a6;margin-top:2px}
.borrow-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #f0f2f5}
.borrow-row:last-child{border-bottom:none}
</style>
