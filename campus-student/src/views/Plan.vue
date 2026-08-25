<template>
  <div>
    <div class="page-head">
      <div><h2>个人培养方案</h2><p>按本专业四年课程设置，修满总学分方可毕业</p></div>
      <el-tag size="large" type="success" effect="plain">总学分 {{ totalCredit }}</el-tag>
    </div>
    <el-empty v-if="!grouped.length" description="暂未配置培养方案" />
    <el-card v-for="g in grouped" :key="g.key" class="year-card" shadow="never">
      <template #header><b>{{ g.label }}</b><span class="credit">学分 {{ g.credit }}</span></template>
      <el-table :data="g.courses" border size="small">
        <el-table-column prop="course_name" label="课程名" />
        <el-table-column prop="course_code" label="编码" width="140" />
        <el-table-column prop="credit" label="学分" width="70" />
        <el-table-column prop="course_type" label="类型" width="120">
          <template #default="{row}">{{ courseTypeMap[row.course_type] || row.course_type }}</template>
        </el-table-column>
        <el-table-column prop="is_required" label="性质" width="90">
          <template #default="{row}"><el-tag size="small" :type="row.is_required==='1'?'danger':'info'">{{ row.is_required==='1'?'必修':'选修' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { useDict } from '@/composables/useDict'
const sid=localStorage.getItem('studentId')||''
const data=ref<any>({totalCredit:0,list:[]})
const courseTypeDict=useDict('course_type')
const courseTypeMap=computed(()=>{ const m:Record<string,string>={}; for(const d of courseTypeDict.value) m[d.dict_value]=d.dict_label; return m })
const termName=['','第一学期','第二学期']
const grouped=computed(()=>{
  const map:Record<string,any>={}
  for(const p of (data.value.list||[])){
    const key=`${p.year_no}-${p.term}`
    if(!map[key]) map[key]={key,label:`第${['一','二','三','四'][p.year_no-1]||p.year_no}学年 · ${termName[p.term]}`,courses:[],credit:0}
    map[key].courses.push(p)
    map[key].credit=(map[key].credit||0)+Number(p.credit||0)
  }
  return Object.values(map)
})
const totalCredit=computed(()=> data.value.totalCredit||0)
async function load(){ const r:any=await request.get('/plan/queryStudentPlan',{params:{studentId:sid}}); data.value=r.data||{totalCredit:0,list:[]} }
onMounted(load)
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.page-head h2{margin:0;font-size:20px}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.year-card{margin-bottom:14px}
.credit{float:right;color:#1e5eff;font-weight:600}
</style>
