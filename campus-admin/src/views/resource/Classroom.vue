<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:10px">
      <h3>教室管理 · 教学楼按学院划分</h3>
      <div style="display:flex;gap:8px;align-items:center">
        <el-select v-model="collegeId" placeholder="按学院筛选" clearable style="width:200px" @change="fetch"><el-option v-for="c in colleges" :key="c.dept_id" :label="c.dept_name" :value="c.dept_id"/></el-select>
        <el-input v-model="roomKw" placeholder="教室编号" clearable style="width:160px" @clear="fetch" @keyup.enter="fetch"/>
        <el-button type="primary" @click="fetch">查询</el-button>
        <el-button type="success" @click="openAdd">新增教室</el-button>
      </div>
    </div>
    <el-table :data="list" border v-loading="loading">
      <el-table-column prop="classroom_id" label="ID" width="80"/>
      <el-table-column label="所属学院" width="200"><template #default="{row}">{{ collegeMap[row.college_id]||row.college_id }}</template></el-table-column>
      <el-table-column prop="room_no" label="教室编号" width="140"/>
      <el-table-column prop="floor" label="楼层" width="80"/>
      <el-table-column prop="capacity" label="容量" width="80"/>
      <el-table-column label="操作" width="140"><template #default="{row}"><el-button size="small" @click="openAdd(row)">编辑</el-button><el-button size="small" type="danger" @click="remove(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50,100]" layout="total,sizes,prev,pager,next" @current-change="fetch" @size-change="fetch"/>

    <el-dialog v-model="dialog" :title="form.classroomId?'编辑教室':'新增教室'" width="460">
      <el-form :model="form" label-width="90px">
        <el-form-item label="所属学院"><el-select v-model="form.collegeId" placeholder="选择学院" style="width:100%"><el-option v-for="c in colleges" :key="c.dept_id" :label="c.dept_name" :value="c.dept_id"/></el-select></el-form-item>
        <el-form-item label="教室编号"><el-input v-model="form.roomNo" placeholder="如 1101 = 学院1+1楼+01室"/></el-form-item>
        <el-form-item label="楼层"><el-input-number v-model="form.floor" :min="1" :max="20"/></el-form-item>
        <el-form-item label="容量"><el-input-number v-model="form.capacity" :min="1" :max="300"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const loading=ref(false)
const list=ref<any[]>([])
const colleges=ref<any[]>([])
const collegeMap=ref<Record<number,string>>({})
const collegeId=ref<number|null>(null)
const roomKw=ref('')
const pageNo=ref(1); const pageSize=ref(20); const total=ref(0)
async function loadColleges(){ const r:any=await request.get('/dept/tree'); const cm:Record<number,string>={}; const arr:any[]=[]; const walk=(nodes:any[])=>{ for(const n of nodes){ if(n.parent_id===0||!n.children){ cm[n.dept_id]=n.dept_name; arr.push(n) } if(n.children) walk(n.children) } }; walk(r.data||[]); colleges.value=arr; collegeMap.value=cm }
async function fetch(){
  loading.value=true
  try{ const r:any=await request.post('/classroom/queryByPage',{pageNo:pageNo.value,pageSize:pageSize.value,data:{collegeId:collegeId.value||undefined, roomNo:roomKw.value}}); list.value=r.data.list||[]; total.value=r.data.total||0 }finally{ loading.value=false }
}
const dialog=ref(false)
const form=reactive<any>({classroomId:null,collegeId:null,roomNo:'',floor:1,capacity:50})
function openAdd(row?:any){ if(row){ Object.assign(form,{classroomId:row.classroom_id,collegeId:row.college_id,roomNo:row.room_no,floor:row.floor,capacity:row.capacity}) } else { Object.assign(form,{classroomId:null,collegeId:null,roomNo:'',floor:1,capacity:50}) } dialog.value=true }
async function submit(){
  if(!form.roomNo) return ElMessage.warning('请填写教室编号')
  const body:any={roomNo:form.roomNo, collegeId:form.collegeId||null, floor:form.floor, capacity:form.capacity}
  if(form.classroomId) body.classroomId=form.classroomId
  await request.post('/classroom/save', body); ElMessage.success('保存成功'); dialog.value=false; fetch()
}
async function remove(row:any){
  try{ await ElMessageBox.confirm('确认删除该教室？','删除',{type:'warning'}) }catch{ return }
  await request.post(`/classroom/delete/${row.classroom_id}`); ElMessage.success('已删除'); fetch()
}
onMounted(async()=>{ await loadColleges(); await fetch() })
</script>
