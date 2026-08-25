<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>学业预警 · 挂科/学分进度自动计算</h3>
      <div>
        <el-select v-model="query.warningType" placeholder="类型" clearable style="width:120px;margin-right:6px"><el-option label="挂科预警" value="FAIL"/><el-option label="学分预警" value="CREDIT"/></el-select>
        <el-select v-model="query.handled" placeholder="处理" clearable style="width:110px;margin-right:6px"><el-option label="未处理" value="0"/><el-option label="已处理" value="1"/></el-select>
        <el-input v-model="query.studentId" placeholder="学号" clearable style="width:130px;margin-right:6px"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="warning" :loading="computing" @click="compute">重新计算全校预警</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="student_id" label="学号" width="130"/>
      <el-table-column prop="studentName" label="姓名" width="100"/>
      <el-table-column label="类型" width="110"><template #default="{row}"><el-tag :type="row.warning_type==='FAIL'?'danger':'warning'" size="small">{{ row.warning_type==='FAIL'?'挂科':'学分不足' }}</el-tag></template></el-table-column>
      <el-table-column label="级别" width="90"><template #default="{row}"><el-tag size="small" :type="row.level>=3?'danger':row.level===2?'warning':'info'">{{ ['','提示','警告','严重'][row.level] }}</el-tag></template></el-table-column>
      <el-table-column prop="detail" label="详情" min-width="240"/>
      <el-table-column prop="semester" label="学期" width="120"/>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.handled==='1'?'success':'info'" size="small">{{ row.handled==='1'?'已处理':'未处理' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="100"><template #default="{row}"><el-button v-if="row.handled==='0'" size="small" type="success" @click="handle(row)">标记处理</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange"/>
  </el-card>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const computing = ref(false)
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/warning/queryByPage', {studentId:'', warningType:'', handled:''})
fetch()
async function compute(){
  computing.value=true
  try{ const r:any=await request.post('/warning/compute', {}); ElMessage.success(`已生成 ${r.data.created} 条（挂科${r.data.fail}/学分${r.data.credit}）`); fetch() } finally{ computing.value=false }
}
async function handle(row:any){ await request.post(`/warning/handle/${row.id}`); ElMessage.success('已处理'); fetch() }
</script>
