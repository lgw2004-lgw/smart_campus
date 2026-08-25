<template>
  <div>
    <div class="page-head">
      <div>
        <h2>我的课表</h2>
        <p>按学期与教学周查看已选课程</p>
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
        <el-select v-model="semester" placeholder="选择学期" clearable style="width:180px" @change="onSemesterChange">
          <el-option label="全部学期" value="" />
          <el-option v-for="s in semesterOptions" :key="s" :label="s" :value="s" />
        </el-select>
        <el-select v-model="week" placeholder="教学周" style="width:140px" @change="renderGrid">
          <el-option label="全部周次" value="" />
          <el-option v-for="w in 18" :key="w" :label="`第${w}周`" :value="String(w)" />
        </el-select>
      </div>
    </div>

    <el-empty v-if="!allData.length" description="暂无可显示的课表" />
    <div v-else class="timetable-wrap">
      <table class="timetable">
        <thead>
          <tr>
            <th class="corner">节次</th>
            <th v-for="d in 7" :key="d">周{{ weekMap[d] }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sec in sections" :key="sec">
            <td class="sec-label">第{{ sec }}节</td>
            <td v-for="day in 7" :key="day" class="cell">
              <div v-for="c in getCell(day, sec)" :key="c.scheduleId" class="cell-card">
                <div class="cell-name">{{ c.courseName }}</div>
                <div class="cell-meta">{{ c.teacherName }} · {{ c.roomNo }}</div>
                <div class="cell-week">第{{ c.startWeek }}-{{ c.endWeek }}周 · {{ c.semester }}</div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
const sid=localStorage.getItem('studentId')||''
const allData=ref<any[]>([])
const semester=ref('')
const week=ref('')
const weekMap:Record<number,string>={1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'日'}
const sections=[1,2,3,4,5,6]

const semesterOptions=computed(()=>{
  const set=new Set<string>()
  for(const r of allData.value) if(r.semester) set.add(r.semester)
  if(semester.value && !set.has(semester.value)) set.add(semester.value)
  return Array.from(set)
})

const filtered=computed(()=>{
  let arr=allData.value
  if(semester.value) arr=arr.filter((r:any)=> r.semester===semester.value)
  if(week.value){
    const w=Number(week.value)
    arr=arr.filter((r:any)=> w>=Number(r.startWeek||1) && w<=Number(r.endWeek||18))
  }
  return arr
})

function getCell(day:number, sec:number){
  return filtered.value.filter((r:any)=> Number(r.weekday)===day && String(r.sectionType)===String(sec))
}

async function load(){
  const params:any={ studentId:sid }
  // 先拉全部，再前端按学期/周过滤，支持“全部学期”
  const r:any=await request.get('/scheduling/queryStudentTimetable',{params})
  allData.value=r.data||[]
  // 默认选中当前学期
  if(!semester.value){
    try{ const cur:any=await request.get('/fee/tuition/get'); if(cur?.data?.semester) semester.value=cur.data.semester }catch{}
  }
}
function onSemesterChange(){ /* filtered computed 自动生效 */ }
function renderGrid(){ /* week computed 自动生效 */ }

onMounted(load)
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px;flex-wrap:wrap;gap:10px}
.page-head h2{margin:0;font-size:20px}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.timetable-wrap{overflow:auto;background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:8px}
.timetable{width:100%;border-collapse:collapse;min-width:800px}
.timetable th,.timetable td{border:1px solid #e6ebf5;padding:8px;vertical-align:top;text-align:center}
.timetable th{background:#f6f8ff;font-weight:600;color:#1e5eff}
.corner{width:90px}
.sec-label{background:#fafbff;font-weight:600;color:#333}
.cell{min-height:70px;height:70px}
.cell-card{background:linear-gradient(135deg,#eef3ff,#f6f8ff);border:1px solid #d6e4ff;border-radius:8px;padding:6px;margin-bottom:4px;text-align:left}
.cell-card:last-child{margin-bottom:0}
.cell-name{font-weight:700;font-size:13px;color:#1e2a3a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cell-meta{font-size:12px;color:#5a6b8a;margin-top:2px}
.cell-week{font-size:11px;color:#8a94a6;margin-top:2px}
</style>
