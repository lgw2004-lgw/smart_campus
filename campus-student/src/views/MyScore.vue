<template>
  <div>
    <el-card shadow="never" style="border-radius:14px;background:linear-gradient(135deg,#0b2a6b,#1e5eff);color:#fff">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div><div style="opacity:.9;font-size:13px">我的绩点</div><div style="font-size:32px;font-weight:800;margin-top:4px">{{ gpa }}</div><div style="font-size:12px;opacity:.85">GPA = Σ(分数×学分)/Σ学分</div></div>
        <div style="text-align:right"><div style="font-size:13px;opacity:.9">已修学分</div><div style="font-size:22px;font-weight:700">{{ credits }}</div><div style="font-size:12px;opacity:.85">共 {{ list.length }} 门</div></div>
      </div>
    </el-card>
    <el-card shadow="never" style="border-radius:14px;margin-top:14px">
      <el-table :data="list" border>
        <el-table-column label="课程" width="200"><template #default="{row}">{{ courseMap[row.course_id] || row.course_id }}</template></el-table-column>
        <el-table-column prop="score" label="分数" width="100"><template #default="{row}"><el-tag :type="row.score>=90?'success':row.score>=60?'info':'danger'" effect="plain">{{ row.score }}</el-tag></template></el-table-column>
        <el-table-column prop="gpa_point" label="绩点" width="100"/>
        <el-table-column prop="semester" label="学期" width="140"/>
        <el-table-column prop="create_time" label="时间"/>
      </el-table>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
const sid=localStorage.getItem('studentId')||''
const list=ref<any[]>([])
const courseMap=ref<Record<string,string>>({})
const gpa=computed(()=>{ if(!list.value.length) return '—'; const avg=list.value.reduce((s:any,r:any)=>s+Number(r.gpa_point||0),0)/list.value.length; return avg.toFixed(2) })
const credits=computed(()=> list.value.length*3 ) // 简化
onMounted(async()=>{
  const cRes:any=await request.post('/course/queryByPage', {pageNo:1,pageSize:200,data:{}})
  const m:Record<string,string>={}; for(const c of (cRes.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m
  const res:any=await request.post('/score/queryByPage', {pageNo:1,pageSize:30,data:{studentId:sid}}); list.value=res.data.list||[]
})
</script>
