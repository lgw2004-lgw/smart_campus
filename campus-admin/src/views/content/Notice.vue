<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>公告管理</h3>
      <div><el-input v-model="query.noticeTitle" placeholder="标题" clearable style="width:200px;margin-right:8px"/><el-button type="primary" @click="search">查询</el-button><el-button type="success" @click="openEdit()">新增公告</el-button></div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="notice_id" label="ID" width="90"/>
      <el-table-column prop="notice_title" label="标题"/>
      <el-table-column prop="notice_type" label="类型" width="80"/>
      <el-table-column prop="status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='0'?'success':'info'">{{ row.status==='0'?'正常':'关闭' }}</el-tag></template></el-table-column>
      <el-table-column prop="create_time" label="时间" width="180"/>
      <el-table-column label="操作" width="160"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />
    <el-dialog v-model="dialog" :title="form.noticeId?'编辑公告':'新增公告'" width="600">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.noticeTitle"/></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.noticeType"><el-option label="通知" value="1"/><el-option label="公告" value="2"/></el-select></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="正常" value="0"/><el-option label="关闭" value="1"/></el-select></el-form-item>
        <el-form-item label="内容"><el-input type="textarea" v-model="form.noticeContent" :rows="4"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/notice/queryByPage', {noticeTitle:''})
fetch()
const dialog=ref(false)
const form=reactive<any>({noticeId:'', noticeTitle:'', noticeType:'1', status:'0', noticeContent:''})
function openEdit(row?:any){ if(row){ form.noticeId=row.notice_id; form.noticeTitle=row.notice_title; form.noticeType=row.notice_type; form.status=row.status; form.noticeContent=row.notice_content } else { form.noticeId=''; form.noticeTitle=''; form.noticeType='1'; form.status='0'; form.noticeContent='' } dialog.value=true }
async function submit(){ await request.post('/notice/save', {noticeId:form.noticeId||undefined, noticeTitle:form.noticeTitle, noticeType:form.noticeType, status:form.status, noticeContent:form.noticeContent}); ElMessage.success('保存成功'); dialog.value=false; fetch() }
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除公告「${row.notice_title}」？`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/notice/delete/${row.notice_id}`)
  ElMessage.success('已删除'); fetch()
}
</script>
