<template>
  <el-card shadow="never" style="border-radius:14px">
    <div style="display:flex;justify-content:space-between;align-items:center"><h3 style="margin:0">我的选课</h3><el-tag type="info">{{ list.length }} 门已选</el-tag></div>
    <div class="enroll-list">
      <div class="enroll-card" v-for="r in list" :key="r.enroll_id">
        <div class="enroll-left">
          <div class="course-name">{{ courseMap[r.course_id] || r.course_id }}</div>
          <div class="enroll-id">{{ r.enroll_id }} · {{ r.create_time?.slice(0,19) }}</div>
        </div>
        <div class="enroll-right">
          <el-tag :type="r.status==='0'?'warning':r.status==='1'?'success':'info'" effect="plain">{{ r.status==='0'?'待缴费':r.status==='1'?'已选':'已退' }}</el-tag>
          <el-button size="small" type="danger" plain :disabled="r.status!=='0'" @click="cancel(r)">退选</el-button>
          <el-button size="small" type="primary" :disabled="r.status!=='0'" @click="$router.push('/my-fee')">去缴费</el-button>
        </div>
      </div>
      <el-empty v-if="!list.length" description="暂无选课，快去选课大厅选课吧" />
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const list=ref<any[]>([])
const courseMap=ref<Record<string,string>>({})
async function loadCourseMap(){ const res:any=await request.post('/course/queryByPage', {pageNo:1,pageSize:200,data:{}}); const m:Record<string,string>={}; for(const c of (res.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }
async function fetch(){ const res:any=await request.post('/enrollment/queryByPage', {pageNo:1,pageSize:30,data:{studentId:sid}}); list.value=res.data.list||[] }
onMounted(()=>{ loadCourseMap(); fetch() })
async function cancel(row:any){ await request.post(`/enrollment/cancel/${row.enroll_id}`); ElMessage.success('已退选'); fetch() }
</script>
<style scoped>
.enroll-list{margin-top:12px;display:flex;flex-direction:column;gap:10px}
.enroll-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px 14px;display:flex;justify-content:space-between;align-items:center}
.course-name{font-weight:700}
.enroll-id{font-size:12px;color:#8a94a6;margin-top:2px}
.enroll-right{display:flex;align-items:center;gap:8px}
</style>
