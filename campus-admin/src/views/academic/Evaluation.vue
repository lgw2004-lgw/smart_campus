<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>评教统计 · 学生对已修课程评分（1-5星）</h3>
      <el-button type="primary" @click="fetch">刷新</el-button>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="course_id" label="课程ID" width="180"/>
      <el-table-column label="课程" min-width="160"><template #default="{row}">{{ row.courseName }}</template></el-table-column>
      <el-table-column label="平均评分" width="160">
        <template #default="{row}"><el-rate :model-value="row.avgRating" disabled show-score text-color="#ff9900"/></template>
      </el-table-column>
      <el-table-column prop="cnt" label="评价人数" width="100"/>
      <el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" @click="detail(row)">查看评语</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,prev,pager,next" @current-change="handleCurrentChange"/>

    <el-dialog v-model="dlg" title="课程评语" width="560">
      <div v-for="(r,i) in details" :key="i" style="border-bottom:1px solid #f0f2f5;padding:10px 0">
        <div style="display:flex;justify-content:space-between"><b>{{ r.studentName }}</b><el-rate :model-value="r.rating" disabled size="small"/></div>
        <div style="font-size:13px;color:#555;margin-top:4px">{{ r.comment_text || '未填写评语' }}</div>
      </div>
      <el-empty v-if="!details.length" description="暂无评价"/>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
const { loading, total, pageNo, pageSize, list, fetch, handleCurrentChange } = usePage('/evaluation/queryByPage', {})
fetch()
const dlg=ref(false); const details=ref<any[]>([])
async function detail(row:any){
  const res:any = await request.get('/evaluation/detail', {params:{courseId:row.course_id}})
  details.value=res.data||[]; dlg.value=true
}
</script>
