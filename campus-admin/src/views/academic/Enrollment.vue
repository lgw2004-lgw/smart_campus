<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>选课管理</h3>
      <div>
        <el-input v-model="query.studentId" placeholder="学号" clearable style="width:160px;margin-right:8px"/>
        <el-select v-model="query.status" placeholder="状态" clearable style="width:140px;margin-right:8px"><el-option label="待缴费" value="0"/><el-option label="已选" value="1"/><el-option label="已退" value="2"/></el-select>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="dialogAdd=true">选课</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="enroll_id" label="选课ID" width="190"/>
      <el-table-column prop="student_id" label="学号" width="120"/>
      <el-table-column label="课程" width="160"><template #default="{row}">{{ courseMap[row.course_id] || row.course_id }}</template></el-table-column>
      <el-table-column prop="schedule_id" label="排课ID" width="90"/>
      <el-table-column prop="status" label="状态" width="90"><template #default="{row}"><el-tag :type="row.status==='0'?'warning':row.status==='1'?'success':'info'">{{ row.status==='0'?'待缴费':row.status==='1'?'已选':'已退' }}</el-tag></template></el-table-column>
      <el-table-column prop="create_time" label="时间"/>
      <el-table-column label="操作" width="220"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" :disabled="row.status!=='0'" @click="cancel(row)">退选</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialogAdd" :title="editId?'编辑选课':'选课'" width="520">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="学号"><el-input v-model="addForm.studentId" placeholder="20240101" :disabled="!!editId"/></el-form-item>
        <el-form-item label="课程"><el-select v-model="addForm.courseId" placeholder="选择课程" filterable style="width:100%" :disabled="!!editId"><el-option v-for="c in selectable" :key="c.course_id" :label="`${c.course_name} (${c.course_id})`" :value="c.course_id"/></el-select><el-button v-if="!editId" size="small" style="margin-top:8px" @click="loadSelectable">加载可选课程</el-button></el-form-item>
        <el-form-item label="排课ID"><el-input v-model="addForm.scheduleId" placeholder="可留空" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogAdd=false">取消</el-button><el-button type="primary" @click="doEnroll">{{ editId?'保存修改':'提交选课' }}</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/enrollment/queryByPage', {studentId:'', status:''})
fetch()
const courseMap=ref<Record<string,string>>({})
async function loadCourseMap(){ const res:any=await request.post('/course/queryByPage', {pageNo:1,pageSize:200,data:{}}); const m:Record<string,string>={}; for(const c of (res.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }
onMounted(loadCourseMap)
const dialogAdd=ref(false)
const editId=ref('')
const addForm=reactive<any>({studentId:'20240101', courseId:'', scheduleId:''})
function openEdit(row:any){
  editId.value=row.enroll_id
  addForm.studentId=row.student_id
  addForm.courseId=row.course_id
  addForm.scheduleId=row.schedule_id||''
  dialogAdd.value=true
}
const selectable=ref<any[]>([])
async function loadSelectable(){
  if(!addForm.studentId) return ElMessage.warning('先填学号')
  const res:any = await request.get('/course/querySelectable', {params:{studentId:addForm.studentId}})
  selectable.value=res.data||[]
  if(!selectable.value.length) ElMessage.info('无可选课程或已全选')
}
async function doEnroll(){
  if(editId.value){
    await request.post('/enrollment/update', {enrollId:editId.value, scheduleId:addForm.scheduleId||null})
    ElMessage.success('已保存修改'); dialogAdd.value=false; editId.value=''; fetch()
    return
  }
  if(!addForm.studentId||!addForm.courseId) return ElMessage.warning('学号课程必填')
  await request.post('/enrollment/add', {studentId:addForm.studentId, courseId:addForm.courseId, scheduleId:addForm.scheduleId||null})
  ElMessage.success('选课成功，待缴费'); dialogAdd.value=false; fetch()
}
async function cancel(row:any){
  await request.post(`/enrollment/cancel/${row.enroll_id}`)
  ElMessage.success('已退选'); fetch()
}
</script>
