<template>
  <el-card>
    <el-tabs>
      <el-tab-pane label="登录日志">
        <el-table :data="loginList" v-loading="loginLoading" border>
          <el-table-column prop="info_id" label="ID" width="90"/>
          <el-table-column prop="user_name" label="用户" width="120"/>
          <el-table-column prop="login_account" label="账号" width="140"/>
          <el-table-column prop="ip_addr" label="IP" width="140"/>
          <el-table-column prop="login_status" label="状态" width="80"><template #default="{row}">{{ row.login_status==='0'?'成功':'失败' }}</template></el-table-column>
          <el-table-column prop="login_time" label="时间"/>
        </el-table>
        <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="loginPage.pageNo" v-model:page-size="loginPage.pageSize" :total="loginTotal" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="fetchLogin" @size-change="fetchLogin" />
      </el-tab-pane>
      <el-tab-pane label="操作日志">
        <el-table :data="operList" v-loading="operLoading" border>
          <el-table-column prop="oper_id" label="ID" width="90"/>
          <el-table-column prop="title" label="标题" width="150"/>
          <el-table-column prop="oper_name" label="操作人" width="120"/>
          <el-table-column prop="oper_url" label="URL"/>
          <el-table-column prop="oper_time" label="时间" width="180"/>
        </el-table>
        <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="operPage.pageNo" v-model:page-size="operPage.pageSize" :total="operTotal" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="fetchOper" @size-change="fetchOper" />
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
const loginList=ref<any[]>([]); const loginLoading=ref(false); const loginTotal=ref(0); const loginPage=reactive({pageNo:1,pageSize:10})
async function fetchLogin(){ loginLoading.value=true; const res:any = await request.post('/loginInfo/queryByPage', {pageNo:loginPage.pageNo,pageSize:loginPage.pageSize,data:{}}); loginList.value=res.data.list||[]; loginTotal.value=res.data.total||0; loginLoading.value=false }
const operList=ref<any[]>([]); const operLoading=ref(false); const operTotal=ref(0); const operPage=reactive({pageNo:1,pageSize:10})
async function fetchOper(){ operLoading.value=true; const res:any = await request.post('/operLog/queryByPage', {pageNo:operPage.pageNo,pageSize:operPage.pageSize,data:{}}); operList.value=res.data.list||[]; operTotal.value=res.data.total||0; operLoading.value=false }
onMounted(()=>{ fetchLogin(); fetchOper() })
</script>
