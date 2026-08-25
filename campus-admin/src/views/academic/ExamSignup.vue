<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>补考报名 · 学生端报名并缴费，此处查看与审核</h3>
      <div>
        <el-input v-model="query.studentId" placeholder="学号" clearable style="width:140px;margin-right:6px"/>
        <el-select v-model="query.status" placeholder="状态" clearable style="width:120px;margin-right:6px"><el-option label="待缴费" value="0"/><el-option label="已报名" value="1"/><el-option label="已取消" value="2"/></el-select>
        <el-button type="primary" @click="search">查询</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="signup_id" label="报名号" width="160"/>
      <el-table-column prop="student_id" label="学号" width="120"/>
      <el-table-column label="课程" min-width="130"><template #default="{row}">{{ row.courseName }}</template></el-table-column>
      <el-table-column label="考试" min-width="150"><template #default="{row}">{{ row.examName }}</template></el-table-column>
      <el-table-column prop="fee_order_id" label="缴费订单" width="150"/>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="['warning','success','info'][Number(row.status)]" size="small">{{ ['待缴费','已报名','已取消'][Number(row.status)] }}</el-tag></template></el-table-column>
      <el-table-column prop="create_time" label="报名时间" width="160"/>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange"/>
  </el-card>
</template>
<script setup lang="ts">
import { usePage } from '@/composables/usePage'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/examSignup/queryByPage', {studentId:'', status:''})
fetch()
</script>
