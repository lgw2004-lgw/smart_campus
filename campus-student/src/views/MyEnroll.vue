<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <h3 style="margin:0">我的选课</h3>
      <el-tag type="info">{{ enriched.length }} 门已选</el-tag>
    </div>
    <div class="course-grid">
      <div class="course-card" v-for="e in enriched" :key="e.enroll_id">
        <div class="card-top">
          <div style="flex:1"><div class="c-name">{{ e.courseName }}</div><div class="c-code">{{ e.courseCode }} · {{ e.hours }}学时</div></div>
          <el-tag size="small" effect="plain">{{ courseTypeMap[e.courseType] || e.courseType }}</el-tag>
          <el-tag size="small" :type="e.status==='2'?'info':'success'" effect="plain" style="margin-left:6px">{{ e.status==='2'?'已退':'已选' }}</el-tag>
        </div>
        <div class="c-meta"><span>开课院系：{{ e.collegeName || e.collegeId }}</span><span>教室：{{ e.roomNo || '待定' }}</span></div>
        <div class="c-meta"><span>教师：{{ e.teacherName || '待定' }}</span><span>周{{ weekMap[e.weekday] || '-' }} 第{{ e.sectionType || '-' }}节 · 第{{ e.startWeek }}-{{ e.endWeek }}周 · {{ e.semester || '' }}</span></div>
        <div class="c-meta"><span>{{ e.credit }}学分 · {{ e.semester || '' }}</span><span style="font-size:12px;color:#8a94a6">{{ e.enroll_id.slice(0,14) }}</span></div>
        <div class="c-foot">
          <span style="font-size:12px;color:#8a94a6">{{ e.create_time?.slice(0,16) }}</span>
          <el-button size="small" type="danger" plain :disabled="e.status==='2'" @click="cancel(e)">退选</el-button>
        </div>
      </div>
      <el-empty v-if="!enriched.length" description="暂无选课，快去选课大厅选课吧" style="grid-column:1/-1" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { useDict } from '@/composables/useDict'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const list=ref<any[]>([])
const courseMapFull=ref<Record<string,any>>({})
const scheduleMap=ref<Record<string,any>>({})
const teacherMap=ref<Record<string,string>>({})
const roomMap=ref<Record<string,string>>({})
const collegeMap=ref<Record<string,string>>({})
const courseTypeDict=useDict('course_type')
const courseTypeMap=computed(()=>{ const m:Record<string,string>={}; for(const d of courseTypeDict.value) m[d.dict_value]=d.dict_label; return m })
const weekMap:Record<string,string>={1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'日'}

const enriched=computed(()=>{
  return list.value.map((r:any)=>{
    const c=courseMapFull.value[r.course_id] || {}
    const s=r.schedule_id ? scheduleMap.value[r.schedule_id] : null
    return {
      ...r,
      courseName: c.course_name || r.course_id,
      courseCode: c.course_code || '-',
      hours: c.hours || '-',
      credit: c.credit ?? '-',
      courseType: c.course_type || '',
      collegeId: c.dept_id || '',
      collegeName: collegeMap.value[c.dept_id] || String(c.dept_id||''),
      teacherName: s ? (teacherMap.value[s.teacher_id]||s.teacher_id) : '',
      roomNo: s ? (roomMap.value[s.classroom_id]||s.classroom_id) : '',
      weekday: s?.weekday,
      sectionType: s?.section_type,
      startWeek: s?.start_week,
      endWeek: s?.end_week,
      semester: s?.semester || '',
    }
  })
})

async function loadAll(){
  const [enrollRes, courseRes, schedRes] = await Promise.all([
    request.post('/enrollment/queryByPage', {pageNo:1,pageSize:50,data:{studentId:sid}}),
    request.post('/course/queryByPage', {pageNo:1,pageSize:2000,data:{}}),
    request.post('/scheduling/selectWithConditions', {}),
  ])
  list.value=(enrollRes as any)?.data?.list || []
  const cm:Record<string,any>={}
  for(const c of (((courseRes as any)?.data?.list)||[])) cm[c.course_id]=c
  courseMapFull.value=cm
  const sm:Record<string,any>={}
  for(const s of (((schedRes as any)?.data)||[])) sm[s.id]=s
  scheduleMap.value=sm
  try{
    const u:any=await request.post('/user/queryByPage',{pageNo:1,pageSize:2000,data:{userType:'1'}})
    const tm:Record<string,string>={}
    for(const x of (u.data.list||[])) tm[x.user_id]=x.user_name
    const u2:any=await request.post('/user/queryByPage',{pageNo:1,pageSize:2000,data:{userType:'8'}})
    for(const x of (u2.data.list||[])) tm[x.user_id]=x.user_name
    teacherMap.value=tm
  }catch{}
  try{
    const r:any=await request.post('/classroom/queryByPage',{pageNo:1,pageSize:2000,data:{}})
    const rm:Record<string,string>={}
    for(const x of (r.data.list||[])) rm[x.classroom_id]=x.room_no
    roomMap.value=rm
  }catch{}
  try{
    const d:any=await request.get('/dept/tree')
    const mp:Record<string,string>={}
    const walk=(arr:any[])=>{ for(const n of arr){ mp[n.dept_id]=n.dept_name; if(n.children) walk(n.children)} }
    walk(d.data||[])
    collegeMap.value=mp
  }catch{}
}
async function cancel(row:any){
  await request.post(`/enrollment/cancel/${row.enroll_id}`)
  ElMessage.success('已退选')
  loadAll()
}
onMounted(loadAll)
</script>
<style scoped>
.course-grid{display:flex;flex-direction:column;gap:10px}
.course-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;align-items:stretch;gap:8px;transition:.2s}
.course-card:hover{box-shadow:0 6px 16px rgba(30,94,255,.10)}
.card-top{display:flex;gap:10px;align-items:center;}
.c-name{font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.c-code{font-size:12px;color:#8a94a6}
.c-meta{display:flex;gap:12px;align-items:center;font-size:12px;color:#5a6b8a;background:#f6f8ff;padding:6px 10px;border-radius:999px;white-space:nowrap}
.c-foot{display:flex;justify-content:space-between;align-items:center;gap:8px}
</style>
