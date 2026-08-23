<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>班级管理</h3>
      <div>
        <el-input v-model="query.className" placeholder="班级名" clearable style="width:200px;margin-right:8px"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openEdit()">新增班级</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="class_id" label="班级ID" width="90"/>
      <el-table-column prop="class_name" label="班级名"/>
      <el-table-column label="所属专业" width="180"><template #default="{row}">{{ deptMap[row.dept_id] || row.dept_id }}</template></el-table-column>
      <el-table-column prop="grade" label="年级" width="100"/>
      <el-table-column label="班主任" width="140"><template #default="{row}">{{ teacherMap[row.head_teacher_id] || (row.head_teacher_id ? '教师#'+row.head_teacher_id : '-') }}</template></el-table-column>
      <el-table-column label="操作" width="160"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />
    <el-dialog v-model="dialog" title="班级" width="480">
      <el-form :model="form" label-width="90px">
        <el-form-item label="班级名"><el-input v-model="form.className"/></el-form-item>
        <el-form-item label="所属专业"><el-tree-select v-model="form.deptId" :data="deptTree" :props="{label:'dept_name', value:'dept_id', children:'children'}" placeholder="选择专业" clearable check-strictly style="width:100%" /></el-form-item>
        <el-form-item label="年级"><el-input v-model="form.grade" type="number" placeholder="2024"/></el-form-item>
        <el-form-item label="班主任"><el-select v-model="form.headTeacherId" placeholder="选择教师" clearable filterable style="width:100%"><el-option v-for="t in teacherOptions" :key="t.user_id" :label="`${t.user_name}${t.phone?' ('+t.phone+')':''}`" :value="t.user_id" /></el-select></el-form-item>
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
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/class/queryByPage', {className:''})
fetch()
const deptTree=ref<any[]>([])
const deptMap=ref<Record<string,string>>({})
async function loadDepts(){ const res:any=await request.get('/dept/tree'); deptTree.value=res.data||[]; const m:Record<string,string>={}; const dfs=(arr:any[])=>{ for(const d of arr){ m[d.dept_id]=d.dept_name; if(d.children) dfs(d.children) } }; dfs(deptTree.value); deptMap.value=m }
const teacherOptions=ref<any[]>([])
const teacherMap=ref<Record<string,string>>({})
async function loadTeachers(){ const res:any=await request.post('/user/queryByPage', {pageNo:1,pageSize:100,data:{userType:'1'}}); const lst=res.data.list||[]; teacherOptions.value=lst; const m:Record<string,string>={}; for(const t of lst) m[t.user_id]=t.user_name; teacherMap.value=m }
onMounted(()=>{ loadDepts(); loadTeachers() })
const dialog=ref(false)
const form=reactive<any>({classId:'',className:'',deptId:'',grade:'',headTeacherId:''})
function openEdit(row?:any){ if(row){ form.classId=row.class_id; form.className=row.class_name; form.deptId=row.dept_id; form.grade=row.grade; form.headTeacherId=row.head_teacher_id } else { form.classId=''; form.className=''; form.deptId=''; form.grade=''; form.headTeacherId='' } dialog.value=true }
async function submit(){ if(!form.className) return ElMessage.warning('必填'); await request.post('/class/save', {classId:form.classId||undefined, className:form.className, deptId:form.deptId?Number(form.deptId):null, grade:form.grade?Number(form.grade):null, headTeacherId:form.headTeacherId?Number(form.headTeacherId):null}); ElMessage.success('保存成功'); dialog.value=false; fetch() }
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除班级「${row.class_name}」？班级下学生将变为无班级`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/class/delete/${row.class_id}`)
  ElMessage.success('已删除'); fetch()
}
// 后端未提供 /class/save 独立接口，复用简单提示：实际应走 academic_app 扩展；此处演示用 class/queryByPage 的创建通过直接调用后端预留
</script>
