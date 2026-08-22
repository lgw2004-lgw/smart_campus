<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>图书管理 · 图书/借阅/归还/逾期罚金</h3>
      <div>
        <el-input v-model="query.bookName" placeholder="书名" clearable style="width:180px;margin-right:6px"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openEdit()">新增图书</el-button>
        <el-button @click="fetchBorrow">借阅记录</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="book_id" label="ID" width="80"/>
      <el-table-column prop="book_name" label="书名"/>
      <el-table-column prop="isbn" label="ISBN" width="150"/>
      <el-table-column prop="author" label="作者" width="110"/>
      <el-table-column prop="category" label="分类" width="90"/>
      <el-table-column prop="stock" label="库存" width="80"><template #default="{row}"><el-tag :type="row.stock>0?'success':'danger'">{{ row.stock }}/{{ row.total }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="280"><template #default="{row}"><el-button size="small" type="primary" :disabled="row.stock<=0" @click="openBorrow(row)">借阅</el-button><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-dialog v-model="dialog" :title="form.bookId?'编辑图书':'新增图书'" width="520">
      <el-form :model="form" label-width="90px">
        <el-form-item label="书名"><el-input v-model="form.bookName"/></el-form-item>
        <el-form-item label="ISBN"><el-input v-model="form.isbn"/></el-form-item>
        <el-form-item label="作者"><el-input v-model="form.author"/></el-form-item>
        <el-form-item label="分类"><el-input v-model="form.category" placeholder="如 计算机/文学"/></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="总量"><el-input-number v-model="form.total" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submitBook">保存</el-button></template>
    </el-dialog>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="borrowDialog" title="借阅" width="420">
      <el-form :model="borrowForm" label-width="80px">
        <el-form-item label="学号"><el-input v-model="borrowForm.studentId" placeholder="20240101"/></el-form-item>
        <el-form-item label="图书ID"><el-input :value="borrowForm.bookId" disabled/></el-form-item>
      </el-form>
      <template #footer><el-button @click="borrowDialog=false">取消</el-button><el-button type="primary" @click="doBorrow">借出</el-button></template>
    </el-dialog>

    <el-card style="margin-top:16px" v-if="showBorrow">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <h4>借阅记录</h4>
        <div><el-input v-model="borrowQuery.studentId" placeholder="学号" clearable style="width:140px;margin-right:6px"/><el-button size="small" @click="fetchBorrow">查询</el-button></div>
      </div>
      <el-table :data="borrowList" v-loading="borrowLoading" border>
        <el-table-column prop="borrow_id" label="借阅ID" width="190"/>
        <el-table-column prop="student_id" label="学号" width="110"/>
        <el-table-column prop="book_id" label="图书ID" width="80"/>
        <el-table-column prop="status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='0'?'warning':row.status==='1'?'success':'danger'">{{ row.status==='0'?'借出':row.status==='1'?'已还':'逾期' }}</el-tag></template></el-table-column>
        <el-table-column prop="due_time" label="应还" width="170"/>
        <el-table-column prop="fine" label="罚金" width="80"/>
        <el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" :disabled="row.status==='1'" @click="doReturn(row)">归还</el-button></template></el-table-column>
      </el-table>
    </el-card>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/book/queryByPage', {bookName:''})
fetch()
const dialog=ref(false)
const form=reactive<any>({bookId:'', bookName:'', isbn:'', author:'', category:'', stock:10, total:10})
function openEdit(row?:any){
  if(row){ form.bookId=row.book_id; form.bookName=row.book_name; form.isbn=row.isbn; form.author=row.author; form.category=row.category; form.stock=row.stock; form.total=row.total }
  else{ form.bookId=''; form.bookName=''; form.isbn=''; form.author=''; form.category=''; form.stock=10; form.total=10 }
  dialog.value=true
}
async function submitBook(){
  if(!form.bookName) return ElMessage.warning('书名必填')
  await request.post('/book/save', {bookId:form.bookId||undefined, bookName:form.bookName, isbn:form.isbn, author:form.author, category:form.category, stock:form.stock, total:form.total})
  ElMessage.success('保存成功'); dialog.value=false; fetch()
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除图书「${row.book_name}」？`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/book/delete/${row.book_id}`)
  ElMessage.success('已删除'); fetch()
}
const borrowDialog=ref(false)
const borrowForm=reactive<any>({studentId:'20240101', bookId:''})
function openBorrow(row:any){ borrowForm.bookId=row.book_id; borrowDialog.value=true }
async function doBorrow(){ await request.post('/borrow/add', {studentId:borrowForm.studentId, bookId:borrowForm.bookId}); ElMessage.success('借阅成功，30天后应还'); borrowDialog.value=false; fetch(); fetchBorrow() }

// 借阅记录
const showBorrow=ref(true)
const borrowLoading=ref(false)
const borrowList=ref<any[]>([])
const borrowQuery=reactive<any>({studentId:''})
async function fetchBorrow(){
  borrowLoading.value=true
  try{
    const res:any = await request.post('/borrow/queryByPage', {pageNo:1, pageSize:20, data:{studentId:borrowQuery.studentId||undefined}})
    borrowList.value=res.data.list||[]
  } finally{ borrowLoading.value=false }
}
async function doReturn(row:any){ const res:any = await request.post(`/borrow/return/${row.borrow_id}`); ElMessage.success(`已归还，罚金 ${res.data.fine} 元`); fetchBorrow(); fetch() }
fetchBorrow()
</script>
