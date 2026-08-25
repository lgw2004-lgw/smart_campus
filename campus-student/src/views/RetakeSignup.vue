<template>
  <div>
    <div class="page-head"><div><h2>补考报名</h2><p>挂科课程可报名对应补考场次，报名后需完成缴费</p></div></div>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><span style="font-weight:700">可报名的补考/重修场次</span></template>
      <el-table :data="exams" border>
        <el-table-column prop="exam_name" label="考试" min-width="150"/>
        <el-table-column label="课程" min-width="130"><template #default="{row}">{{ courseMap[row.course_id]||row.course_id }}</template></el-table-column>
        <el-table-column label="类型" width="80"><template #default="{row}">{{ typeMap[row.exam_type] }}</template></el-table-column>
        <el-table-column label="日期时间" width="170"><template #default="{row}">{{ row.exam_date }} {{ row.start_time }}~{{ row.end_time }}</template></el-table-column>
        <el-table-column label="教室" width="90"><template #default="{row}">{{ row.room_no||'待定' }}</template></el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button size="small" type="primary" :disabled="signedExamIds.has(row.exam_id)" @click="signup(row)">{{ signedExamIds.has(row.exam_id)?'已报名':'报名' }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!exams.length" description="暂无可报名的补考场次"/>
    </el-card>

    <el-card shadow="never" style="border-radius:14px;margin-top:14px">
      <template #header><span style="font-weight:700">我的报名记录</span></template>
      <div v-for="r in signups" :key="r.signup_id" class="bar">
        <div style="flex:1;min-width:0">
          <div style="font-weight:600">{{ r.examName || r.exam_id }} · {{ r.courseName || r.course_id }}</div>
          <div style="font-size:12px;color:#8a94a6;margin-top:2px">订单 {{ r.fee_order_id || '—' }} · {{ r.create_time?.slice(0,19) }}</div>
        </div>
        <el-tag :type="['warning','success','info'][Number(r.status)]" effect="plain">{{ ['待缴费','已报名','已取消'][Number(r.status)] }}</el-tag>
        <el-button v-if="r.status==='0'" size="small" type="success" @click="payConfirm(r)">确认支付</el-button>
        <el-button v-if="r.status==='0'" size="small" @click="cancel(r)">取消</el-button>
      </div>
      <el-empty v-if="!signups.length" description="暂无报名记录"/>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const exams=ref<any[]>([]); const signups=ref<any[]>([])
const courseMap=ref<Record<string,string>>({})
const typeMap:Record<string,string>={'2':'补考','3':'重修'}
const signedExamIds=computed(()=>new Set(signups.value.filter(s=>s.status!=='2').map(s=>s.exam_id)))
async function loadCourses(){ try{ const r:any=await request.post('/course/queryByPage',{pageNo:1,pageSize:500,data:{}}); const m:Record<string,string>={}; for(const c of (r.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }catch{} }
async function loadExams(){
  try{
    const r:any=await request.post('/exam/queryByPage',{pageNo:1,pageSize:100,data:{status:'1', examType:'2'}})
    const list=r.data.list||[]
    // 仅显示本人挂科的课程
    const sc:any=await request.post('/score/queryByPage',{pageNo:1,pageSize:200,data:{studentId:sid}})
    const failed=new Set((sc.data.list||[]).filter((x:any)=>Number(x.score)<60 && x.exam_type==='0').map((x:any)=>x.course_id))
    exams.value=list.filter((e:any)=>failed.has(e.course_id))
  }catch{}
}
async function loadSignups(){ const r:any=await request.post('/examSignup/queryByPage',{pageNo:1,pageSize:50,data:{studentId:sid}}); signups.value=r.data.list||[] }
async function signup(row:any){
  const res:any=await request.post('/examSignup/add', {studentId:sid, examId:row.exam_id})
  ElMessage.success(`已提交报名，费用 ¥${res.data.fee}，请确认支付`)
  loadSignups()
}
async function payConfirm(r:any){ await request.post(`/examSignup/payConfirm/${r.signup_id}`); ElMessage.success('支付成功，已完成报名'); loadSignups() }
async function cancel(r:any){ await request.post(`/examSignup/cancel/${r.signup_id}`); ElMessage.success('已取消'); loadSignups() }
onMounted(async()=>{ await loadCourses(); await loadExams(); await loadSignups() })
</script>
<style scoped>
.page-head{margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.bar{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid #e6ebf5;border-radius:12px;margin-bottom:10px;background:#fff}
.bar:hover{box-shadow:0 6px 16px rgba(30,94,255,.10)}
</style>
