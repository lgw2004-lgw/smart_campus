<template>
  <div>
    <div class="page-head"><div><h2>请假申请</h2><p>提交后由班级辅导员审批</p></div></div>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><span style="font-weight:700">发起申请</span></template>
      <el-form inline>
        <el-form-item label="类型"><el-select v-model="form.leaveType" style="width:100px"><el-option v-for="t in ['事假','病假','其他']" :key="t" :label="t" :value="t"/></el-select></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.startDate" type="date" value-format="YYYY-MM-DD"/></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.endDate" type="date" value-format="YYYY-MM-DD"/></el-form-item>
        <el-form-item label="事由"><el-input v-model="form.reason" style="width:260px" maxlength="200"/></el-form-item>
        <el-form-item><el-button type="primary" @click="apply">提交申请</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="border-radius:14px;margin-top:14px">
      <template #header><span style="font-weight:700">我的申请记录</span></template>
      <div v-for="r in rows" :key="r.leave_id" class="bar">
        <div style="flex:1;min-width:0">
          <div style="font-weight:600">{{ r.leave_type }} · {{ r.start_date }} ~ {{ r.end_date }}</div>
          <div style="font-size:12px;color:#8a94a6;margin-top:2px">辅导员：{{ r.headTeacherName || '待分配' }} · 事由：{{ r.reason }}</div>
        </div>
        <el-tag :type="['warning','success','danger','info'][Number(r.status)]" effect="plain">{{ ['待审批','已批准','已驳回','已撤回'][Number(r.status)] }}</el-tag>
        <el-button v-if="r.status==='0'" size="small" @click="cancel(r)">撤回</el-button>
      </div>
      <el-empty v-if="!rows.length" description="暂无申请记录"/>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const rows=ref<any[]>([])
const form=reactive<any>({leaveType:'事假', startDate:'', endDate:'', reason:''})
async function load(){ const r:any=await request.post('/leave/queryByPage',{pageNo:1,pageSize:50,data:{studentId:sid}}); rows.value=r.data.list||[] }
async function apply(){
  if(!form.startDate||!form.endDate||!form.reason) return ElMessage.warning('请完整填写日期与事由')
  if(form.endDate<form.startDate) return ElMessage.warning('结束日期不能早于开始日期')
  await request.post('/leave/apply', {studentId:sid, ...form})
  ElMessage.success('已提交，等待辅导员审批'); form.reason=''; load()
}
async function cancel(r:any){ try{ await ElMessageBox.confirm('确认撤回该申请？','撤回',{type:'warning'}) }catch{ return }
  await request.post(`/leave/cancel/${r.leave_id}`); ElMessage.success('已撤回'); load() }
onMounted(load)
</script>
<style scoped>
.page-head{margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.bar{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid #e6ebf5;border-radius:12px;margin-bottom:10px;background:#fff}
.bar:hover{box-shadow:0 6px 16px rgba(30,94,255,.10)}
</style>
