<template>
  <div>
    <div class="page-head"><div><h2>考试信息</h2><p>已发布且与已选课程相关的考试安排</p></div>
      <div style="display:flex;gap:8px;align-items:center">
        <el-select v-model="query.semester" placeholder="学期" clearable style="width:160px" @change="onSearch"><el-option v-for="s in semesters" :key="s" :label="s" :value="s"/></el-select>
        <el-button type="primary" @click="onSearch">查询</el-button>
      </div>
    </div>
    <el-card v-for="r in list" :key="r.exam_id" shadow="never" style="margin-bottom:10px;border-radius:12px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div style="font-weight:700">{{ r.exam_name }} <el-tag size="small" style="margin-left:6px">{{ typeMap[r.exam_type]||r.exam_type }}</el-tag></div>
          <div style="font-size:13px;color:#606266;margin-top:4px">{{ courseMap[r.course_id]||r.course_id }} · {{ r.semester }}</div>
          <div style="font-size:12px;color:#909399;margin-top:4px">{{ r.exam_date }} {{ r.start_time }} ~ {{ r.end_time }} · 教室 {{ r.room_no || '待定' }}</div>
        </div>
        <el-tag type="success" effect="plain">已发布</el-tag>
      </div>
    </el-card>
    <el-empty v-if="!list.length" description="暂无考试安排" />
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="fetch" @size-change="fetch" />
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
const sid = localStorage.getItem('studentId') || ''
const list=ref<any[]>([]); const total=ref(0); const pageNo=ref(1); const pageSize=ref(10)
const query=reactive<any>({semester:''})
const semesters=ref<string[]>(['2024-2025-1','2024-2025-2','2025-2026-1','2025-2026-2'])
const courseMap=ref<Record<string,string>>({})
const typeMap:Record<string,string>={ '0':'期中','1':'期末','2':'补考','3':'重修'}
async function loadCourses(){ try{ const res:any=await request.post('/course/queryByPage',{pageNo:1,pageSize:500,data:{}}); const m:Record<string,string>={}; for(const c of (res.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }catch{} }
async function fetch(){
  const res:any=await request.post('/exam/queryStudentExams',{pageNo:pageNo.value,pageSize:pageSize.value,data:{studentId:sid, semester:query.semester||undefined}})
  list.value=res.data.list||[]; total.value=res.data.total||0
}
function onSearch(){ pageNo.value=1; fetch() }
onMounted(async()=>{ await loadCourses(); await fetch() })
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
</style>
