<template>
  <div>
    <!-- 顶部横幅 -->
    <div class="hero">
      <div class="hero-left">
        <div class="greet">早上好，{{ name }} 同学 👋</div>
        <h2>今天也要元气满满地学习！</h2>
        <p>待办：{{ pending }} 门待缴费 · 有新公告 2 条 · 图书应还 1 本</p>
        <div class="actions">
          <el-button type="primary" round @click="$router.push('/courses')">去选课</el-button>
          <el-button round plain @click="$router.push('/my-fee')">去缴费</el-button>
        </div>
      </div>
      <div class="hero-right">
        <el-carousel height="160px" v-if="banners.length" indicator-position="outside" style="border-radius:12px;overflow:hidden">
          <el-carousel-item v-for="b in banners" :key="b.id"><img :src="b.url" style="width:100%;height:160px;object-fit:cover"/><div class="banner-title">{{ b.name }}</div></el-carousel-item>
        </el-carousel>
      </div>
    </div>

    <!-- 快捷服务 -->
    <div class="section-title"><span>快捷服务</span><el-link type="primary" :underline="false">全部服务</el-link></div>
    <div class="grid">
      <div class="svc" v-for="s in services" :key="s.path" @click="$router.push(s.path)">
        <div class="svc-icon" :style="{background:s.bg, color:s.color}"><el-icon :size="24"><component :is="s.icon"/></el-icon></div>
        <div class="svc-title">{{ s.title }}</div>
        <div class="svc-desc">{{ s.desc }}</div>
        <div v-if="s.badge" class="svc-badge">{{ s.badge }}</div>
      </div>
    </div>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card class="card" shadow="never">
          <template #header><div class="card-head"><span>最新公告</span><el-link type="primary" @click="$router.push('/notices')">更多</el-link></div></template>
          <div v-for="n in notices" :key="n.notice_id" class="notice-item">
            <div class="dot"></div>
            <div style="flex:1"><div class="n-title">{{ n.notice_title }}</div><div class="n-time">{{ n.create_time?.slice(0,10) }} · 教务处</div></div>
            <el-tag size="small" :type="n.status==='0'?'success':'info'">{{ n.notice_type==='2'?'公告':'通知' }}</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card class="card" shadow="never">
          <template #header><div class="card-head"><span>我的课表 · 今日</span><span style="font-size:12px;color:#8a94a6">3月周二</span></div></template>
          <div class="schedule">
            <div class="sch" v-for="sch in schedule" :key="sch.time"><div class="sch-time">{{ sch.time }}</div><div class="sch-box" :style="{background:sch.bg}"><div style="font-weight:600">{{ sch.course }}</div><div style="font-size:12px;opacity:.8">{{ sch.room }} · {{ sch.teacher }}</div></div></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
const sid=localStorage.getItem('studentId')||''; const name=localStorage.getItem('studentName')||''
const banners=ref<any[]>([]); const notices=ref<any[]>([]); const pending=ref(0)
const services=[
  {title:'选课大厅', desc:'可选 12 门', path:'/courses', icon:'Reading', bg:'#eef3ff', color:'#1e5eff', badge:'选课中'},
  {title:'一卡通缴费', desc:'待缴 1 笔', path:'/my-fee', icon:'Wallet', bg:'#fff4e6', color:'#ff7e00', badge:''},
  {title:'宿舍服务', desc:'学3栋 301', path:'/my-dorm', icon:'OfficeBuilding', bg:'#e6f7ff', color:'#0ea5e9', badge:''},
  {title:'图书借阅', desc:'在借 2 本', path:'/my-book', icon:'Notebook', bg:'#f0fdf4', color:'#16a34a', badge:''},
  {title:'成绩查询', desc:'GPA 3.4', path:'/my-score', icon:'DataAnalysis', bg:'#fef2f2', color:'#e11d48', badge:''},
  {title:'通知公告', desc:'2 条未读', path:'/notices', icon:'Bell', bg:'#f5f3ff', color:'#7c3aed', badge:''},
]
const schedule=[
  {time:'08:00 1-2节', course:'高等数学', room:'教学楼 A101', teacher:'王老师', bg:'#eef3ff'},
  {time:'10:00 3-4节', course:'数据结构', room:'实验楼 202', teacher:'李老师', bg:'#fff4e6'},
  {time:'14:00 5-6节', course:'大学英语', room:'外语楼 305', teacher:'张老师', bg:'#f0fdf4'},
]
onMounted(async()=>{
  const r:any=await request.get('/banner/loadBanner'); banners.value=r.data||[]
  const r2:any=await request.post('/notice/queryByPage', {pageNo:1,pageSize:5,data:{}}); notices.value=r2.data.list||[]
  const r3:any=await request.post('/enrollment/queryByPage', {pageNo:1,pageSize:20,data:{studentId:sid, status:'0'}}); pending.value=r3.data.total||0
})
</script>
<style scoped>
.hero{background:linear-gradient(135deg,#1e5eff 0%,#5b8cff 100%);border-radius:16px;padding:18px 20px;color:#fff;display:flex;gap:18px;align-items:center}
.hero-left{flex:1}
.greet{font-size:13px;opacity:.9}
.hero-left h2{margin:6px 0 8px;font-size:22px;font-weight:800}
.hero-left p{opacity:.9;font-size:13px}
.actions{margin-top:12px}
.hero-right{width:380px}
.banner-title{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(0,0,0,.55));color:#fff;padding:8px 10px;font-size:13px}
.section-title{margin-top:16px;display:flex;justify-content:space-between;align-items:center;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-top:10px}
.svc{background:#fff;border:1px solid #e6ebf5;border-radius:14px;padding:14px;text-align:center;cursor:pointer;position:relative;transition:.2s}
.svc:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(30,94,255,.12)}
.svc-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px}
.svc-title{font-weight:600;font-size:13px}
.svc-desc{font-size:12px;color:#8a94a6;margin-top:2px}
.svc-badge{position:absolute;top:8px;right:8px;background:#ff4d4f;color:#fff;font-size:10px;padding:2px 6px;border-radius:999px}
.card{border-radius:14px;border:1px solid #e6ebf5}
.card-head{display:flex;justify-content:space-between;align-items:center;font-weight:700}
.notice-item{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f0f2f5}
.notice-item:last-child{border-bottom:none}
.dot{width:8px;height:8px;background:#1e5eff;border-radius:50%}
.n-title{font-weight:600;font-size:13px}
.n-time{font-size:12px;color:#8a94a6}
.schedule{display:flex;flex-direction:column;gap:10px}
.sch{display:flex;gap:10px;align-items:center}
.sch-time{width:90px;font-size:12px;color:#8a94a6}
.sch-box{flex:1;padding:10px;border-radius:10px}
</style>
