<template>
  <div class="login-root">
    <div class="left">
      <div class="brand">
        <div class="logo-icon">校</div>
        <div>
          <div class="brand-title">智慧校园</div>
          <div class="brand-sub">SMART CAMPUS</div>
        </div>
      </div>
      <div class="hero">
        <div class="hero-tag">学生服务大厅 · Student Portal</div>
        <h1>一个账号<br/>通办校园所有事</h1>
        <p>选课 · 缴费 · 宿舍 · 图书 · 成绩 · 公告，一站式办理。后台数据与教务、财务、宿舍实时联动。</p>
        <div class="stats">
          <div class="stat"><div class="num">1,234</div><div class="lab">在校生</div></div>
          <div class="stat"><div class="num">89</div><div class="lab">今日选课</div></div>
          <div class="stat"><div class="num">12</div><div class="lab">待缴费</div></div>
        </div>
        <div class="illus">
          <div class="card c1">📚 图书借阅</div>
          <div class="card c2">🏫 宿舍选择</div>
          <div class="card c3">💳 一卡通缴费</div>
          <div class="card c4">📊 成绩查询</div>
        </div>
      </div>
      <div class="footer">© 2024-2025 智慧校园 · 管理后台仅限教师/领导 http://127.0.0.1:5173</div>
    </div>
    <div class="right">
      <el-card class="login-card" shadow="never">
        <div class="card-head">
          <h2>学生登录</h2>
          <p>学号登录 · 初始密码 123456</p>
        </div>
        <el-form :model="form" @submit.prevent="onLogin" label-position="top">
          <el-form-item label="学号"><el-input v-model="form.id" placeholder="如 20240101" prefix-icon="User" size="large" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="form.pwd" type="password" placeholder="123456" prefix-icon="Lock" show-password size="large" /></el-form-item>
          <el-form-item><el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;height:44px;font-size:16px">登录学生端</el-button></el-form-item>
          <div class="tips">
            <span>测试账号：20240101 / 123456</span>
            <el-link type="primary" :underline="false" @click="$router.push('/login')">忘记密码?</el-link>
          </div>
        </el-form>
        <div class="divider"><span>联动说明</span></div>
        <div class="link-box">
          <div>管理后台（教师/领导）</div>
          <el-link type="primary" href="http://127.0.0.1:5173" target="_blank">http://127.0.0.1:5173 → admin/123456</el-link>
          <div style="margin-top:6px;color:#999;font-size:12px">同一后端 127.0.0.1:18367 · 数据实时同步</div>
        </div>
      </el-card>
    </div>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
const router=useRouter(); const auth=useAuthStore()
const loading=ref(false)
const form=reactive({id:'20240101', pwd:'123456'})
async function onLogin(){ loading.value=true; try{ await auth.login(form.id, form.pwd); ElMessage.success('欢迎回来'); router.push('/home') } catch(e:any){ ElMessage.error(e.message||'登录失败') } finally{ loading.value=false } }
</script>
<style scoped>
.login-root{height:100vh;display:flex;background:#f0f5ff}
.left{flex:1.2;background:linear-gradient(135deg,#0b2a6b 0%,#1e5eff 45%,#5b8cff 100%);color:#fff;padding:28px 40px;display:flex;flex-direction:column;position:relative;overflow:hidden}
.left::after{content:'';position:absolute;right:-80px;top:120px;width:420px;height:420px;background:rgba(255,255,255,.08);border-radius:50%}
.brand{display:flex;align-items:center;gap:12px}
.logo-icon{width:44px;height:44px;background:#fff;color:#1e5eff;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:22px}
.brand-title{font-size:18px;font-weight:800}
.brand-sub{font-size:11px;letter-spacing:2px;opacity:.8}
.hero{margin-top:48px;max-width:520px}
.hero-tag{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.2);display:inline-block;padding:4px 12px;border-radius:999px;font-size:12px;margin-bottom:16px}
.hero h1{font-size:40px;line-height:1.15;font-weight:900;margin:0}
.hero p{margin-top:14px;opacity:.9;line-height:1.6}
.stats{display:flex;gap:18px;margin-top:20px}
.stat{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.15);padding:12px 16px;border-radius:12px;min-width:90px;text-align:center}
.num{font-size:22px;font-weight:800}
.lab{font-size:12px;opacity:.8}
.illus{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:22px}
.illus .card{background:#fff;color:#1e3a5f;padding:12px;border-radius:12px;font-weight:600;box-shadow:0 8px 20px rgba(0,0,0,.12)}
.illus .c1{transform:rotate(-1deg)} .illus .c2{transform:rotate(1deg)} .illus .c3{transform:rotate(1deg)} .illus .c4{transform:rotate(-1deg)}
.footer{margin-top:auto;font-size:12px;opacity:.7}
.right{flex:.9;display:flex;align-items:center;justify-content:center;padding:24px;background:#f0f5ff}
.login-card{width:420px;border-radius:16px;border:1px solid #e6ebf5;box-shadow:0 10px 30px rgba(16,48,120,.12)}
.card-head h2{margin:0;font-size:22px}
.card-head p{color:#8a94a6;margin:6px 0 0}
.tips{display:flex;justify-content:space-between;font-size:12px;color:#8a94a6}
.divider{margin:18px 0;display:flex;align-items:center;gap:12px;color:#8a94a6;font-size:12px}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#e6ebf5}
.link-box{background:#f6f8ff;border:1px solid #e6ebf5;border-radius:10px;padding:10px;font-size:13px}
</style>
