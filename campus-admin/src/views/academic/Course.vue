<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>课程管理</h3>
      <div>
        <el-input v-model="query.courseName" placeholder="课程名" clearable style="width:200px;margin-right:8px" @clear="search" @keyup.enter="search"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openEdit()">新增课程</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="course_id" label="课程ID" width="170"/>
      <el-table-column prop="course_name" label="课程名"/>
      <el-table-column prop="course_code" label="编码"/>
      <el-table-column prop="credit" label="学分" width="80"/>
      <el-table-column prop="hours" label="学时" width="80"/>
      <el-table-column prop="status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='0'?'success':'info'">{{ row.status==='0'?'正常':'停用' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="160"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />
    <el-dialog v-model="dialog" :title="form.courseId?'编辑课程':'新增课程'" width="520">
      <el-form :model="form" label-width="80px">
        <el-form-item label="课程名"><el-input v-model="form.courseName" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="form.courseCode" placeholder="留空自动生成" /></el-form-item>
        <el-form-item label="学分"><el-input-number v-model="form.credit" :min="0.5" :max="10" :step="0.5" /></el-form-item>
        <el-form-item label="学时"><el-input-number v-model="form.hours" :min="1" :max="200" /></el-form-item>
        <el-form-item label="所属院系"><el-tree-select v-model="form.deptId" :data="deptTree" :props="{label:'dept_name', value:'dept_id', children:'children'}" placeholder="选择所属学院/专业" clearable check-strictly style="width:100%" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="正常" value="0"/><el-option label="停用" value="1"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/course/queryByPage', {courseName:''})
fetch()
const deptTree=ref<any[]>([])
async function loadDepts(){ const res:any=await request.get('/dept/tree'); deptTree.value=res.data||[] }
onMounted(loadDepts)
const dialog=ref(false)
const form=reactive<any>({courseId:'',courseName:'',courseCode:'',credit:3,hours:48,deptId:'',status:'0'})
function openEdit(row?:any){
  if(row){ form.courseId=row.course_id; form.courseName=row.course_name; form.courseCode=row.course_code; form.credit=Number(row.credit); form.hours=row.hours; form.deptId=row.dept_id; form.status=row.status }
  else{ form.courseId=''; form.courseName=''; form.courseCode=''; form.credit=3; form.hours=48; form.deptId=''; form.status='0' }
  dialog.value=true
}
async function submit(){
  if(!form.courseName) return ElMessage.warning('课程名必填')
  await request.post('/course/save', {courseId:form.courseId||undefined, courseName:form.courseName, courseCode:form.courseCode||undefined, credit:form.credit, hours:form.hours, deptId:form.deptId||null, status:form.status})
  ElMessage.success('保存成功'); dialog.value=false; fetch()
}
async function removeRow(row:any){
  try{
    await ElMessageBox.confirm(`确认直接删除课程「${row.course_name}」？此操作不可恢复`, '删除确认', {type:'warning', confirmButtonText:'删除', cancelButtonText:'取消'})
  } catch{ return }
  await request.post(`/course/delete/${row.course_id}`)
  ElMessage.success('已删除'); fetch()
}
</script>
