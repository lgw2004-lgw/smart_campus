<template>
  <div>
    <div class="page-head"><div><h2>考勤签到</h2><p>输入教师提供的签到码完成课堂签到</p></div></div>
    <el-card shadow="never" style="border-radius:14px">
      <div style="display:flex;gap:10px;align-items:center">
        <el-input v-model="code" placeholder="6位签到码" maxlength="6" style="width:200px" @keyup.enter="signIn"/>
        <el-button type="primary" :loading="signing" @click="signIn">签到</el-button>
      </div>
    </el-card>
    <el-card shadow="never" style="border-radius:14px;margin-top:14px">
      <template #header><span style="font-weight:700">我的考勤记录</span></template>
      <el-table :data="rows" border>
        <el-table-column label="课程" min-width="150"><template #default="{row}">{{ row.courseName || row.course_id }}</template></el-table-column>
        <el-table-column prop="schedule_id" label="排课" width="90"/>
        <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.attend_status==='1'?'success':'danger'" size="small">{{ row.attend_status==='1'?'已到':'缺勤' }}</el-tag></template></el-table-column>
        <el-table-column prop="create_time" label="时间" width="170"/>
      </el-table>
      <el-empty v-if="!rows.length" description="暂无考勤记录"/>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const code=ref(''); const signing=ref(false); const rows=ref<any[]>([])
async function load(){ const r:any=await request.get('/attendance/myStats',{params:{studentId:sid}}); rows.value=r.data||[] }
async function signIn(){
  if(!code.value) return ElMessage.warning('请输入签到码')
  signing.value=true
  try{
    await request.post('/attendance/signIn', {studentId:sid, code:code.value})
    ElMessage.success('签到成功'); code.value=''; load()
  }catch{} finally{ signing.value=false }
}
onMounted(load)
</script>
<style scoped>
.page-head{margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
</style>
