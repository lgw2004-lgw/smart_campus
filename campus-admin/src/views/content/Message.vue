<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>消息管理 · 发送站内消息推送到学生端</h3>
      <div>
        <el-input v-model="query.title" placeholder="标题搜索" clearable style="width:160px;margin-right:6px"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="dlg=true">发送消息</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="message_id" label="ID" width="150"/>
      <el-table-column prop="title" label="标题" min-width="180"/>
      <el-table-column prop="content" label="内容" min-width="240"/>
      <el-table-column prop="msg_type" label="类型" width="90"/>
      <el-table-column label="对象" width="120"><template #default="{row}">{{ row.target_type==='0'?'全体学生':('指定 '+row.target_id) }}</template></el-table-column>
      <el-table-column prop="create_time" label="时间" width="160"/>
      <el-table-column label="操作" width="90"><template #default="{row}"><el-button size="small" type="danger" @click="del(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange"/>

    <el-dialog v-model="dlg" title="发送消息" width="520">
      <el-form label-width="100px">
        <el-form-item label="类型">
          <el-select v-model="form.msgType" style="width:100%"><el-option label="系统" value="SYS"/><el-option label="成绩" value="SCORE"/><el-option label="考试" value="EXAM"/><el-option label="缴费" value="FEE"/><el-option label="宿舍" value="DORM"/></el-select>
        </el-form-item>
        <el-form-item label="接收对象">
          <el-radio-group v-model="form.targetType"><el-radio value="0">全体学生</el-radio><el-radio value="1">指定学号</el-radio></el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.targetType==='1'" label="学号"><el-input v-model="form.targetStudentId"/></el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title"/></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="4"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg=false">取消</el-button><el-button type="primary" @click="send">发送</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/message/queryByPage', {title:''})
fetch()
const dlg=ref(false)
const form=reactive({msgType:'SYS', targetType:'0', targetStudentId:'', title:'', content:''})
async function send(){
  if(!form.title||!form.content) return ElMessage.warning('标题与内容必填')
  if(form.targetType==='1' && !form.targetStudentId) return ElMessage.warning('请填写学号')
  await request.post('/message/send', form)
  ElMessage.success('已发送'); dlg.value=false; Object.assign(form,{msgType:'SYS',targetType:'0',targetStudentId:'',title:'',content:''}); fetch()
}
async function del(row:any){ try{ await ElMessageBox.confirm(`删除消息「${row.title}」？`,'删除',{type:'warning'}) }catch{ return }
  await request.post(`/message/delete/${row.message_id}`); ElMessage.success('已删除'); fetch() }
</script>
