<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>考勤管理 · 教师发起签到场次，学生输码签到</h3>
      <div>
        <el-input v-model="query.courseId" placeholder="课程ID" clearable style="width:150px;margin-right:6px"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openCreate">发起签到</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="id" label="场次" width="80"/>
      <el-table-column label="课程" min-width="140"><template #default="{row}">{{ row.courseName }}</template></el-table-column>
      <el-table-column label="签到码" width="110"><template #default="{row}"><span style="font-weight:800;font-size:16px;color:#1e5eff">{{ row.session_code }}</span></template></el-table-column>
      <el-table-column prop="start_time" label="开始" width="160"/>
      <el-table-column prop="end_time" label="截止" width="160"/>
      <el-table-column label="出勤/应到" width="110"><template #default="{row}"><el-tag :type="row.total&&row.present>=row.total?'success':'warning'" size="small">{{ row.present }}/{{ row.total }}</el-tag></template></el-table-column>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.status==='0'?'success':'info'" size="small">{{ row.status==='0'?'进行中':'已结束' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{row}">
          <el-button size="small" :disabled="row.status!=='0'" type="warning" @click="close(row)">结束签到</el-button>
          <el-button size="small" @click="showRoster(row)">名单</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,prev,pager,next" @current-change="handleCurrentChange"/>

    <el-dialog v-model="dlg" title="发起签到场次" width="480">
      <el-form label-width="100px">
        <el-form-item label="排课ID"><el-input-number v-model="form.scheduleId" :min="1" style="width:100%"/></el-form-item>
        <el-form-item label="时长(分钟)"><el-input-number v-model="form.minutes" :min="1" :max="120" style="width:100%"/></el-form-item>
        <el-form-item v-if="createdCode" label="签到码"><div style="font-size:32px;font-weight:900;color:#1e5eff;letter-spacing:8px">{{ createdCode }}</div><div style="font-size:12px;color:#999">学生端输入该码完成签到，{{ form.minutes }} 分钟内有效</div></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg=false">关闭</el-button><el-button v-if="!createdCode" type="primary" @click="create">生成签到码</el-button></template>
    </el-dialog>

    <el-dialog v-model="rosterDlg" title="出勤名单" width="520">
      <el-table :data="roster" size="small" border max-height="400">
        <el-table-column prop="student_id" label="学号" width="130"/>
        <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.attend_status==='1'?'success':'danger'" size="small">{{ row.attend_status==='1'?'已到':'缺勤' }}</el-tag></template></el-table-column>
        <el-table-column prop="create_time" label="时间"/>
      </el-table>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, search } = usePage('/attendance/session/queryByPage', {courseId:''})
fetch()
const dlg=ref(false); const createdCode=ref('')
const form=reactive({scheduleId:1, minutes:5})
function openCreate(){ createdCode.value=''; dlg.value=true }
async function create(){
  const res:any = await request.post('/attendance/session/create', {scheduleId:form.scheduleId, minutes:form.minutes})
  createdCode.value=res.data.code; ElMessage.success('已生成'); fetch()
}
async function close(row:any){ await request.post(`/attendance/session/close/${row.id}`); ElMessage.success('已结束'); fetch() }
const rosterDlg=ref(false); const roster=ref<any[]>([])
async function showRoster(row:any){
  const res:any = await request.post('/attendance/queryByPage', {pageNo:1,pageSize:200,data:{sessionId:row.id}})
  roster.value=res.data.list||[]; rosterDlg.value=true
}
</script>
