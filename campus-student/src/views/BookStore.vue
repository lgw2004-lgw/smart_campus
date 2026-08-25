<template>
  <div>
    <div class="page-head"><div style="display:flex;gap:12px;align-items:center"><el-button @click="router.push('/my-book')">返回图书馆</el-button><div><h2>书库</h2><p>与管理端库存联动 · 借阅30天 逾期 0.5元/天</p></div></div><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><el-input v-model="kw" placeholder="搜索书名" prefix-icon="Search" style="width:220px" clearable @clear="onSearch" @keyup.enter="onSearch" /><el-select v-model="category" placeholder="类型筛选" clearable filterable style="width:160px" @change="onSearch"><el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" /></el-select><el-button type="primary" @click="onSearch">搜索</el-button></div></div>
    <div class="book-grid">
      <div class="book-card" v-for="b in books" :key="b.book_id">
        <div style="flex:1;min-width:0"><div class="book-name">{{ b.book_name }}</div><div class="book-meta">{{ b.author }} · {{ b.category }} · ISBN {{ b.isbn }}</div><div style="margin-top:6px"><el-tag :type="b.stock>0?'success':'danger'" size="small" effect="plain">{{ b.stock }}/{{ b.total }} 可借</el-tag></div></div>
        <el-button type="primary" size="small" round :disabled="b.stock<=0" @click="borrow(b)">借阅</el-button>
      </div>
    </div>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="loadBooks" @size-change="loadBooks" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const router=useRouter()
const sid=localStorage.getItem('studentId')||''
const books=ref<any[]>([]); const kw=ref(''); const category=ref(''); const categoryOptions=ref<string[]>([]); const pageNo=ref(1); const pageSize=ref(10); const total=ref(0)
async function loadCategories(){
  try{
    const res:any=await request.post('/book/queryByPage', {pageNo:1,pageSize:2000,data:{}})
    const set=new Set<string>()
    for(const b of (res.data.list||[])) if(b.category) set.add(b.category)
    categoryOptions.value=Array.from(set).sort()
  }catch{}
}
async function loadBooks(){ const data:any={}; if(kw.value) data.bookName=kw.value; if(category.value) data.category=category.value; const res:any=await request.post('/book/queryByPage', {pageNo:pageNo.value,pageSize:pageSize.value,data}); books.value=res.data.list||[]; total.value=res.data.total||0 }
function onSearch(){ pageNo.value=1; loadBooks() }
async function borrow(row:any){ await request.post('/borrow/add', {studentId:sid, bookId:row.book_id}); ElMessage.success('借阅成功'); loadBooks() }
onMounted(async()=>{ await loadCategories(); await loadBooks() })
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.book-grid{display:flex;flex-direction:column;gap:10px}
.book-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px 16px;display:flex;gap:12px;align-items:center;transition:.2s}
.book-card:hover{box-shadow:0 6px 16px rgba(30,94,255,.10)}
.book-name{font-weight:700}
.book-meta{font-size:12px;color:#8a94a6;margin-top:2px}
</style>
