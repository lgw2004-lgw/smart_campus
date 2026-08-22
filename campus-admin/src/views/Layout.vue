<template>
  <el-container style="height:100vh">
    <el-aside width="220px" style="background:#001529;overflow:auto">
      <div style="color:#fff;text-align:center;padding:16px;font-size:18px;font-weight:bold">智慧校园</div>
      <el-menu router :default-active="$route.path" background-color="#001529" text-color="#ccc" active-text-color="#409EFF" unique-opened>
        <el-menu-item index="/home"><el-icon><House /></el-icon>首页看板</el-menu-item>
        <el-sub-menu index="/academic"><template #title><el-icon><Reading /></el-icon>教务管理</template>
          <el-menu-item index="/academic/course">课程管理</el-menu-item>
          <el-menu-item index="/academic/scheduling">排课管理</el-menu-item>
          <el-menu-item index="/academic/enrollment">选课管理</el-menu-item>
          <el-menu-item index="/academic/score">成绩管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/student"><template #title><el-icon><User /></el-icon>学生管理</template>
          <el-menu-item index="/student/list">学生档案</el-menu-item>
          <el-menu-item index="/student/class">班级管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/resource"><template #title><el-icon><Box /></el-icon>资源管理</template>
          <el-menu-item index="/resource/dorm">宿舍管理</el-menu-item>
          <el-menu-item index="/resource/book">图书管理</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/finance/fee"><el-icon><Wallet /></el-icon>财务缴费</el-menu-item>
        <el-sub-menu index="/content"><template #title><el-icon><Document /></el-icon>内容管理</template>
          <el-menu-item index="/content/notice">公告管理</el-menu-item>
          <el-menu-item index="/content/banner">轮播管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/system"><template #title><el-icon><Setting /></el-icon>系统管理</template>
          <el-menu-item index="/system/user">用户管理</el-menu-item>
          <el-menu-item index="/system/role">角色管理</el-menu-item>
          <el-menu-item index="/system/menu">菜单管理</el-menu-item>
          <el-menu-item index="/system/dept">院系管理</el-menu-item>
          <el-menu-item index="/system/dict">字典管理</el-menu-item>
          <el-menu-item index="/system/log">日志管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee">
        <span>{{ $route.meta.title }}</span>
        <div>
          <span style="margin-right:12px">{{ auth.userName }}</span>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main style="background:#f0f2f5;overflow:auto"><router-view /></el-main>
    </el-container>
  </el-container>
</template>
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
const auth = useAuthStore()
const router = useRouter()
function logout() {
  auth.logout()
  router.push('/login')
}
</script>
