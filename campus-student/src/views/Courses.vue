<template>
  <div>
    <div class="page-head">
      <div><h2>选课大厅</h2><p>已发布课程方可选择 · 总学费缴清后直接选课，学费已含课程费用</p></div>
      <div style="display:flex;gap:10px">
        <el-input placeholder="搜索课程名/编码" prefix-icon="Search" style="width:220px" v-model="kw" clearable @clear="load" @keyup.enter="load" />
        <el-input placeholder="搜索教师" prefix-icon="Search" style="width:180px" v-model="teacherKw" clearable @clear="load" @keyup.enter="load" />
      </div>
    </div>
    <div class="course-grid">
      <div class="course-card" v-for="c in list" :key="c.scheduleId">
        <div class="card-top">
          <div style="flex:1"><div class="c-name">{{ c.courseName }}</div><div class="c-code">{{ c.courseCode }} · {{ c.hours }}学时 · {{ c.credit }}学分</div></div>
          <el-tag size="small" effect="plain">{{ courseTypeMap[c.courseType] || c.courseType }}</el-tag>
        </div>
        <div class="c-meta">
          <span>开课院系：{{ c.collegeName || c.collegeId }}</span>
          <span>教室：{{ c.roomNo || '待定' }}</span>
        </div>
        <div class="c-meta">
          <span>教师：{{ c.teacherName || '待定' }}</span>
          <span>周{{ weekMap[c.weekday] }} 第{{ c.sectionType }}节 · 第{{ c.startWeek }}-{{ c.endWeek }}周</span>
        </div>
        <div class="c-meta">
          <span>容量：{{ c.capacity }}</span>
          <span>剩余名额：<b :class="c.remaining>0?'ok':'full'">{{ c.remaining>0?c.remaining:'已满' }}</b></span>
        </div>
        <div class="c-foot">
          <el-button type="primary" round size="small" :disabled="c.remaining<=0" @click="enroll(c)">立即选课</el-button>
        </div>
      </div>
      <el-empty v-if="!list.length" description="暂无可选择的已发布课程" style="grid-column:1/-1" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { useDict } from '@/composables/useDict'
import { ElMessage, ElMessageBox } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const list=ref<any[]>([])
const kw=ref(''); const teacherKw=ref('')
const courseTypeDict=useDict('course_type')
const courseTypeMap=computed(()=>{ const m:Record<string,string>={}; for(const d of courseTypeDict.value) m[d.dict_value]=d.dict_label; return m })
const weekMap:Record<number,string>={1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'日'}
const semester=ref('')
async function getSemester(){ try{ const r:any=await request.get('/fee/tuition/get'); semester.value=r?.data?.semester||'' }catch{} }
async function load(){
  const params:any={ studentId:sid, kw:kw.value, teacherKw:teacherKw.value }
  if(semester.value) params.semester=semester.value
  const res:any=await request.get('/scheduling/querySelectable', { params })
  list.value=res.data||[]
}
async function enroll(row:any){
  try{
    const res:any=await request.post('/enrollment/add', {studentId:sid, scheduleId:row.scheduleId})
    if(res?.data?.isRetake){
      ElMessageBox.alert(`重修课 ${row.courseName} 已选，重修费 ¥${res.data.retakeFee} 订单 ${res.data.retakeOrderId} 已生成，请到“一卡通·缴费”支付`, '重修计费')
    } else {
      ElMessage.success(`已选 ${row.courseName}（总学费已覆盖，无需逐门缴费）`)
    }
    load()
  }catch(e:any){
    const msg=e?.message || e?.response?.data?.message || ''
    if(msg.includes('总学费')) ElMessageBox.alert(msg+'，请先到“一卡通·缴费”缴纳总学费','未缴总学费')
    else if(msg.includes('满')) ElMessage.warning(msg)
    else ElMessage.error(msg||'选课失败')
  }
}
onMounted(async()=>{ await getSemester(); await load() })
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px}
.page-head h2{margin:0;font-size:20px}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.course-grid{display:flex;flex-direction:column;gap:10px}
.course-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:14px 16px;display:flex;align-items:center;gap:16px;transition:.2s;flex-wrap:wrap}
.course-card:hover{box-shadow:0 6px 16px rgba(30,94,255,.10)}
.card-top{display:flex;gap:10px;align-items:center;flex:1;min-width:0}
.c-name{font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.c-code{font-size:12px;color:#8a94a6}
.c-meta{display:flex;gap:12px;align-items:center;font-size:12px;color:#5a6b8a;background:#f6f8ff;padding:6px 10px;border-radius:999px;white-space:nowrap}
.c-foot{flex-shrink:0}
.ok{color:#00a950}.full{color:#ff4d4f}
</style>
