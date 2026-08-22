<template>
  <div>
    <div class="page-head">
      <div><h2>选课大厅</h2><p>已为你过滤已选与时间冲突课程 · 每学分 100元</p></div>
      <el-input placeholder="搜索课程" prefix-icon="Search" style="width:260px" v-model="kw" clearable />
    </div>
    <div class="course-grid">
      <div class="course-card" v-for="c in filtered" :key="c.course_id">
        <div class="card-top">
          <div class="c-icon">{{ c.course_name.slice(0,1) }}</div>
          <div style="flex:1"><div class="c-name">{{ c.course_name }}</div><div class="c-code">{{ c.course_code }} · {{ c.hours }}学时</div></div>
          <el-tag size="small" type="success" effect="plain">{{ c.credit }}学分</el-tag>
        </div>
        <div class="c-meta"><span>开课院系 {{ c.dept_id }}</span><span>剩余名额 充足</span></div>
        <div class="c-foot">
          <span class="price">¥{{ Number(c.credit)*100 }}</span>
          <el-button type="primary" round size="small" @click="enroll(c)">立即选课</el-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const list=ref<any[]>([]); const kw=ref('')
async function load(){ const res:any=await request.get('/course/querySelectable', {params:{studentId:sid}}); list.value=res.data||[] }
const filtered=computed(()=>{ if(!kw.value) return list.value; return list.value.filter((c:any)=>c.course_name.includes(kw.value)||c.course_code.includes(kw.value)) })
async function enroll(row:any){ await request.post('/enrollment/add', {studentId:sid, courseId:row.course_id}); ElMessage.success(`已选 ${row.course_name}，请到“我的选课/缴费”付款`); load() }
onMounted(load)
</script>
<style scoped>
.page-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px}
.page-head h2{margin:0;font-size:20px}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.course-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.course-card{background:#fff;border:1px solid #e6ebf5;border-radius:14px;padding:14px;transition:.2s}
.course-card:hover{box-shadow:0 8px 20px rgba(30,94,255,.12);transform:translateY(-1px)}
.card-top{display:flex;gap:10px;align-items:center}
.c-icon{width:40px;height:40px;background:linear-gradient(135deg,#1e5eff,#5b8cff);color:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800}
.c-name{font-weight:700}
.c-code{font-size:12px;color:#8a94a6}
.c-meta{display:flex;justify-content:space-between;margin-top:10px;font-size:12px;color:#8a94a6;background:#f6f8ff;padding:6px 8px;border-radius:8px}
.c-foot{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.price{font-weight:800;color:#ff7e00}
</style>
