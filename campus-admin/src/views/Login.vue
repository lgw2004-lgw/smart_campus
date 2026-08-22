<template>
  <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f0f2f5">
    <el-card style="width:400px">
      <h2 style="text-align:center">智慧校园 · 管理后台</h2>
      <p style="text-align:center;color:#999;font-size:12px">仅限学校领导/教师登录 · 学生请前往 C端 5174</p>
      <el-form :model="form" @submit.prevent="onLogin">
        <el-form-item><el-input v-model="form.userName" placeholder="用户名" prefix-icon="User" /></el-form-item>
        <el-form-item><el-input v-model="form.password" type="password" placeholder="密码 123456" prefix-icon="Lock" show-password /></el-form-item>
        <el-form-item><el-button type="primary" native-type="submit" :loading="loading" style="width:100%">登录管理后台</el-button></el-form-item>
      </el-form>
      <div style="font-size:12px;color:#999;text-align:center">admin/123456 | teacher01/123456<br/>学生请访问 http://127.0.0.1:5174</div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ userName: 'admin', password: '123456' })

async function onLogin() {
  loading.value = true
  try {
    const data:any = await auth.login(form.userName, form.password, false)
    // 后台仅允许管理/教师（userType 0/1），学生禁止
    if(data.userType==='2' || data.userType===2){
      auth.logout()
      return ElMessage.error('学生请前往 C端 http://127.0.0.1:5174 登录，此后台仅限教师/领导')
    }
    ElMessage.success('登录成功')
    router.push('/home')
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
