<template>
  <div class="student-root">
    <!-- 顶部校级导航 -->
    <div class="top-header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-icon">校</div>
          <div>
            <div class="logo-title">智慧校园 · 学生服务大厅</div>
            <div class="logo-sub">Smart Campus Student Portal</div>
          </div>
        </div>
        <div class="semester-tag">{{ semesterLabel }}</div>
      </div>
      <div class="header-right">
        <el-badge :value="noticeCount" :hidden="noticeCount===0" class="bell" style="cursor:pointer" @click="router.push('/notices')"><el-icon :size="20"><Bell /></el-icon></el-badge>
        <div class="user-card">
          <el-avatar :size="36" style="background:#fff;color:#1e5eff;font-weight:bold">{{ auth.name.slice(0,1) }}</el-avatar>
          <div class="user-info">
            <div class="user-name">{{ auth.name }} 同学</div>
            <div class="user-id">学号 {{ auth.studentId }}</div>
          </div>
            <el-dropdown trigger="click" @command="onCmd">
            <el-icon style="color:#fff;cursor:pointer"><ArrowDown /></el-icon>
            <template #dropdown><el-dropdown-menu><el-dropdown-item command="profile">个人资料</el-dropdown-item><el-dropdown-item command="logout">退出登录</el-dropdown-item></el-dropdown-menu></template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <el-container style="height:calc(100vh - 64px)">
      <el-aside width="250px" class="side">
        <div class="user-panel">
          <div class="avatar-wrap"><el-avatar :size="64" style="background:linear-gradient(135deg,#1e5eff,#5b8cff);color:#fff;font-size:22px">{{ auth.name.slice(0,1) }}</el-avatar><div class="online-dot"></div></div>
          <div class="panel-name">{{ auth.name }}</div>
          <div class="panel-id">{{ auth.studentId }} · 计算机系</div>
          <el-tag size="small" type="success" effect="plain" style="margin-top:6px">在校</el-tag>
        </div>
        <el-menu router :default-active="$route.path" class="side-menu" unique-opened>
          <el-menu-item index="/home"><el-icon><House /></el-icon>校园首页</el-menu-item>
          <el-menu-item index="/courses"><el-icon><Reading /></el-icon>选课大厅<el-tag size="small" style="margin-left:auto" type="warning">选课中</el-tag></el-menu-item>
          <el-menu-item index="/my-enroll"><el-icon><List /></el-icon>我的选课</el-menu-item>
          <el-menu-item index="/timetable"><el-icon><Calendar /></el-icon>我的课表</el-menu-item>
          <el-menu-item index="/plan"><el-icon><Notebook /></el-icon>个人培养方案</el-menu-item>
          <el-menu-item index="/my-fee"><el-icon><Wallet /></el-icon>一卡通·缴费</el-menu-item>
          <el-menu-item index="/my-dorm"><el-icon><OfficeBuilding /></el-icon>宿舍服务</el-menu-item>
          <el-menu-item index="/my-book"><el-icon><Notebook /></el-icon>图书馆</el-menu-item>
          <el-menu-item index="/my-score"><el-icon><DataAnalysis /></el-icon>成绩查询</el-menu-item>
          <el-menu-item index="/profile"><el-icon><User /></el-icon>个人资料</el-menu-item>
          <el-menu-item index="/notices"><el-icon><Bell /></el-icon>通知公告</el-menu-item>
        </el-menu>
        <div class="side-footer">
          <div class="help-card">
            <div style="font-weight:bold">需要帮助？</div>
            <div style="font-size:12px;color:#666;margin:4px 0">辅导员：张老师 138****1234</div>
            <el-button size="small" type="primary" plain>联系帮助</el-button>
          </div>
        </div>
      </el-aside>
      <el-main class="main"><router-view /></el-main>
    </el-container>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
const auth=useAuthStore(); const router=useRouter()
function onCmd(c:string){ if(c==='profile'){ router.push('/profile'); return } if(c==='logout'){ auth.logout(); router.push('/login') } }
const noticeCount=ref(0)
const semesterLabel=ref('2024-2025学年 · 春季学期')
function formatSemester(s:string){
  // 2025-2026-1 -> 2025-2026学年 · 秋季学期, 2025-2026-2 -> 春季
  if(!s) return semesterLabel.value
  const parts=s.split('-')
  if(parts.length===3){ const year=`${parts[0]}-${parts[1]}`; const term=parts[2]==='1'?'秋季学期':parts[2]==='2'?'春季学期':`第${parts[2]}学期`; return `${year}学年 · ${term}` }
  return s
}
onMounted(async()=>{
  try{
    const res:any=await request.get('/fee/tuition/get')
    if(res?.data?.semester) semesterLabel.value=formatSemester(res.data.semester)
  }catch{ /* 保持默认 */ }
  // 同步最新姓名（管理员改名后，旧token里还是旧名）
  try{
    const sid=auth.studentId || localStorage.getItem('studentId')
    if(sid){
      const r:any=await request.get(`/student/queryById/${sid}`)
      if(r?.data?.name && r.data.name!==auth.name){
        auth.name=r.data.name
        localStorage.setItem('studentName', r.data.name)
      }
    }
  }catch{}
  try{
    const r:any=await request.post('/notice/queryByPage', {pageNo:1,pageSize:1,data:{}})
    noticeCount.value=r?.data?.total ?? 0
  }catch{}
})
</script>
<style scoped>
.student-root{height:100vh;background:#f0f5ff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial}
.top-header{height:64px;background:linear-gradient(90deg,#0b2a6b 0%,#1e5eff 55%,#3d7eff 100%);display:flex;align-items:center;justify-content:space-between;padding:0 20px;color:#fff;box-shadow:0 2px 8px rgba(0,0,0,.15)}
.logo{display:flex;align-items:center;gap:12px}
.logo-icon{width:42px;height:42px;background:#fff;color:#1e5eff;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px}
.logo-title{font-size:16px;font-weight:800;letter-spacing:.5px}
.logo-sub{font-size:11px;opacity:.8}
.semester-tag{margin-left:18px;background:rgba(255,255,255,.15);padding:4px 10px;border-radius:999px;font-size:12px;border:1px solid rgba(255,255,255,.2)}
.header-right{display:flex;align-items:center;gap:18px}
.bell{color:#fff;cursor:pointer}
.user-card{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.12);padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.15)}
.user-name{font-size:13px;font-weight:600;line-height:1}
.user-id{font-size:11px;opacity:.8}
.side{background:#fff;border-right:1px solid #e6ebf5;display:flex;flex-direction:column}
.user-panel{text-align:center;padding:18px 12px;border-bottom:1px solid #f0f2f5}
.avatar-wrap{position:relative;display:inline-block}
.online-dot{position:absolute;right:4px;bottom:4px;width:12px;height:12px;background:#00c950;border:2px solid #fff;border-radius:50%}
.panel-name{margin-top:8px;font-weight:700;font-size:15px}
.panel-id{font-size:12px;color:#8a94a6}
.side-menu{border-right:none}
.side-menu :deep(.el-menu-item){margin:4px 8px;border-radius:8px}
.side-menu :deep(.el-menu-item.is-active){background:#eef3ff;color:#1e5eff;font-weight:600}
.side-footer{margin-top:auto;padding:12px}
.help-card{background:#f6f8ff;border:1px solid #e6ebf5;border-radius:12px;padding:12px}
.main{background:#f0f5ff;padding:18px 20px;overflow:auto}
</style>
