<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>请假审批 · 辅导员审批本班学生申请</h3>
      <div>
        <el-select v-model="query.status" placeholder="状态" clearable style="width:120px;margin-right:6px"><el-option label="待审批" value="0"/><el-option label="已批准" value="1"/><el-option label="已驳回" value="2"/><el-option label="已撤回" value="3"/></el-select>
        <el-button type="primary" @click="search">查询</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="student_id" label="学号" width="130"/>
      <el-table-column prop="studentName" label="姓名" width="100"/>
      <el-table-column prop="headTeacherName" label="辅导员" width="100"/>
      <el-table-column prop="leave_type" label="类型" width="80"/>
      <el-table-column prop="start_date" label="开始" width="110"/>
      <el-table-column prop="end_date" label="结束" width="110"/>
      <el-table-column prop="reason" label="事由" min-width="180"/>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="['warning','success','danger','info'][Number(row.status)]" size="small">{{ ['待审批','已批准','已驳回','已撤回'][Number(row.status)] }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{row}">
          <template v-if="row.status==='0' && canApprove(row)">
            <el-button size="small" type="success" @click="act(row,'approve')">批准</el-button>
            <el-button size="small" type="danger" @click="act(row,'reject')">驳回</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange"/>
  </el-card>
</template>
<script setup lang="ts">
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const isAdmin = localStorage.getItem('userType')==='1'
const myId = Number(localStorage.getItem('userId')||0)
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/leave/queryByPage', {status:''})
fetch()
function canApprove(row:any){ return isAdmin || Number(row.head_teacher_id)===myId }
async function act(row:any, action:string){
  let opinion = ''
  if(action==='reject'){
    try{ ({ value: opinion } = await ElMessageBox.prompt('请输入驳回理由', '驳回', {confirmButtonText:'确定', cancelButtonText:'取消'})) }catch{ return }
  } else {
    try{ await ElMessageBox.confirm(`确认批准 ${row.studentName} 的${row.leave_type}申请？`,'批准',{type:'success'}) }catch{ return }
  }
  await request.post('/leave/approve', {leaveId:row.leave_id, action, opinion})
  ElMessage.success('已处理'); fetch()
}
</script>
