<template>
  <div>
    <div class="page-head"><div><h2>课程评教</h2><p>对已修课程进行 1-5 星评价，可修改</p></div></div>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><span style="font-weight:700">待评教课程</span></template>
      <div v-for="c in pending" :key="c.courseId" class="bar">
        <div style="flex:1;min-width:120px"><div style="font-weight:600">{{ c.courseName }}</div></div>
        <el-rate v-model="form[c.courseId]" show-text :texts="['很差','较差','一般','良好','优秀']"/>
        <el-input v-model="comment[c.courseId]" placeholder="评语（可选）" style="width:220px"/>
        <el-button size="small" type="primary" @click="submit(c.courseId)">提交</el-button>
      </div>
      <el-empty v-if="!pending.length" description="全部已选课程均已评价，感谢参与"/>
    </el-card>
    <el-card shadow="never" style="border-radius:14px;margin-top:14px">
      <template #header><span style="font-weight:700">我的历史评价</span></template>
      <el-table :data="mine" border>
        <el-table-column label="课程" min-width="150"><template #default="{row}">{{ courseMap[row.course_id]||row.course_id }}</template></el-table-column>
        <el-table-column label="评分" width="170"><template #default="{row}"><el-rate :model-value="row.rating" disabled/></template></el-table-column>
        <el-table-column prop="comment_text" label="评语" min-width="200"/>
        <el-table-column prop="semester" label="学期" width="120"/>
      </el-table>
      <el-empty v-if="!mine.length" description="暂无历史评价"/>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const pending=ref<any[]>([]); const mine=ref<any[]>([])
const form=reactive<Record<string,number>>({}); const comment=reactive<Record<string,string>>({})
const courseMap=ref<Record<string,string>>({})
async function loadCourses(){ try{ const r:any=await request.post('/course/queryByPage',{pageNo:1,pageSize:500,data:{}}); const m:Record<string,string>={}; for(const c of (r.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }catch{} }
async function loadPending(){
  const r:any=await request.get('/evaluation/pending',{params:{studentId:sid}})
  pending.value=r.data||[]
  for(const c of pending.value) if(!form[c.courseId]) form[c.courseId]=5
}
async function loadMine(){ const r:any=await request.get('/evaluation/my',{params:{studentId:sid}}); mine.value=r.data||[] }
async function submit(courseId:string){
  await request.post('/evaluation/save', {studentId:sid, courseId, rating:form[courseId]||5, comment:comment[courseId]||''})
  ElMessage.success('评价成功'); await Promise.all([loadPending(), loadMine()])
}
onMounted(async()=>{ await loadCourses(); await loadPending(); await loadMine() })
</script>
<style scoped>
.page-head{margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.bar{display:flex;align-items:center;gap:14px;padding:12px;border:1px solid #e6ebf5;border-radius:12px;margin-bottom:10px;background:#fff;flex-wrap:wrap}
</style>
