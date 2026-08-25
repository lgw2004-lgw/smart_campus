<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:10px">
      <h3>排课管理 · 按专业从培养方案排课并发布</h3>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-tree-select v-model="majorId" :data="deptTree" :props="{label:'dept_name',value:'dept_id',children:'children'}" placeholder="选择专业" check-strictly style="width:220px" @change="loadList"/>
        <el-input v-model="semester" placeholder="学期 如 2025-2026-1" style="width:160px"/>
        <el-button type="success" @click="bulk">从培养方案批量排课</el-button>
        <el-button type="primary" @click="publish(true)">发布</el-button>
        <el-button @click="publish(false)">撤回发布</el-button>
        <el-button type="warning" @click="openAdd">手动排课</el-button>
      </div>
    </div>
    <el-table :data="list" border v-loading="loading">
      <el-table-column prop="course_id" label="课程" width="200"><template #default="{row}">{{ courseMap[row.course_id]||row.course_id }}</template></el-table-column>
      <el-table-column label="教师" width="120"><template #default="{row}">{{ teacherMap[row.teacher_id]||row.teacher_id }}</template></el-table-column>
      <el-table-column label="教室" width="110"><template #default="{row}">{{ roomMap[row.classroom_id]||row.classroom_id }}</template></el-table-column>
      <el-table-column label="星期" width="80"><template #default="{row}">周{{ weekMap[row.weekday] }}</template></el-table-column>
      <el-table-column prop="section_type" label="节次" width="70"/>
      <el-table-column label="周次" width="110"><template #default="{row}">第{{ row.start_week }}-{{ row.end_week }}周</template></el-table-column>
      <el-table-column prop="capacity" label="容量" width="70"/>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.is_published==='1'?'success':'info'" size="small">{{ row.is_published==='1'?'已发布':'未发布' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="140"><template #default="{row}"><el-button size="small" @click="openAdd(row)">编辑</el-button><el-button size="small" type="danger" @click="remove(row)">删除</el-button></template></el-table-column>
    </el-table>

    <el-dialog v-model="dialog" :title="form.id?'编辑排课':'手动排课'" width="520">
      <el-form :model="form" label-width="90px">
        <el-form-item label="课程"><el-select v-model="form.courseId" filterable placeholder="选择课程" style="width:100%"><el-option v-for="c in courseOptions" :key="c.course_id" :label="c.course_name" :value="c.course_id"/></el-select></el-form-item>
        <el-form-item label="教师"><el-select v-model="form.teacherId" filterable placeholder="选择教师" style="width:100%"><el-option v-for="t in teacherOptions" :key="t.user_id" :label="t.user_name" :value="t.user_id"/></el-select></el-form-item>
        <el-form-item label="教室"><el-select v-model="form.classroomId" filterable placeholder="选择教室" style="width:100%"><el-option v-for="r in roomOptions" :key="r.classroom_id" :label="r.room_no" :value="r.classroom_id"/></el-select></el-form-item>
        <el-form-item label="星期"><el-select v-model="form.weekday" style="width:100%"><el-option v-for="d in 5" :key="d" :label="`周${weekMap[d]}`" :value="d"/></el-select></el-form-item>
        <el-form-item label="节次"><el-input-number v-model="form.sectionType" :min="1" :max="6"/></el-form-item>
        <el-form-item label="起始周"><el-input-number v-model="form.startWeek" :min="1" :max="18"/></el-form-item>
        <el-form-item label="结束周"><el-input-number v-model="form.endWeek" :min="1" :max="18"/></el-form-item>
        <el-form-item label="容量"><el-input-number v-model="form.capacity" :min="1" :max="200"/></el-form-item>
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
const deptTree=ref<any[]>([])
const majorId=ref<number|null>(null)
const semester=ref('')
const list=ref<any[]>([])
const weekMap:Record<number,string>={1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'日'}
const courseMap=ref<Record<string,string>>({})
const teacherMap=ref<Record<number,string>>({})
const roomMap=ref<Record<number,string>>({})
const courseOptions=ref<any[]>([])
const teacherOptions=ref<any[]>([])
const roomOptions=ref<any[]>([])

async function loadMeta(){
  const c:any=await request.post('/course/queryByPage',{pageNo:1,pageSize:2000,data:{}}); const cm:Record<string,string>={}; for(const x of (c.data.list||[])) cm[x.course_id]=x.course_name; courseMap.value=cm; courseOptions.value=c.data.list||[]
  const u1:any=await request.post('/user/queryByPage',{pageNo:1,pageSize:2000,data:{userType:'1'}}); const tm:Record<number,string>={}; for(const x of (u1.data.list||[])) tm[x.user_id]=x.user_name; teacherMap.value=tm; teacherOptions.value=u1.data.list||[]
  const u8:any=await request.post('/user/queryByPage',{pageNo:1,pageSize:2000,data:{userType:'8'}}); for(const x of (u8.data.list||[])) tm[x.user_id]=x.user_name; teacherOptions.value=[...teacherOptions.value, ...(u8.data.list||[])]
  const r:any=await request.post('/classroom/queryByPage',{pageNo:1,pageSize:2000,data:{}}); const rm:Record<number,string>={}; for(const x of (r.data.list||[])) rm[x.classroom_id]=x.room_no; roomMap.value=rm; roomOptions.value=r.data.list||[]
  const t:any=await request.get('/dept/tree'); deptTree.value=t.data||[]
  try{ const f:any=await request.get('/fee/tuition/get'); semester.value=f?.data?.semester||'2025-2026-1' }catch{ semester.value='2025-2026-1' }
}
async function loadList(){
  if(!majorId.value||!semester.value) return
  loading.value=true
  try{
    const res:any=await request.post('/scheduling/selectWithConditions',{majorId:majorId.value, semester:semester.value})
    list.value=res.data||[]
  }finally{ loading.value=false }
}
async function bulk(){
  if(!majorId.value||!semester.value) return ElMessage.warning('请选择专业与学期')
  const r:any=await request.post('/scheduling/bulkForMajor',{majorId:majorId.value, semester:semester.value})
  if(r.code===200){ ElMessage.success(`已排 ${r.data.made} 门必修课`); loadList() } else ElMessage.error(r.message||'排课失败')
}
async function publish(p:boolean){
  if(!majorId.value||!semester.value) return ElMessage.warning('请选择专业与学期')
  await request.post('/scheduling/publish',{majorId:majorId.value, semester:semester.value, published: p?'1':'0'})
  ElMessage.success(p?'已发布':'已撤回'); loadList()
}
const dialog=ref(false)
const form=reactive<any>({id:null,courseId:'',teacherId:'',classroomId:'',weekday:1,sectionType:1,startWeek:1,endWeek:18,capacity:50})
function openAdd(row?:any){
  if(row){ Object.assign(form,{id:row.id,courseId:row.course_id,teacherId:row.teacher_id,classroomId:row.classroom_id,weekday:row.weekday,sectionType:Number(row.section_type),startWeek:row.start_week,endWeek:row.end_week,capacity:row.capacity}) }
  else{ Object.assign(form,{id:null,courseId:'',teacherId:'',classroomId:'',weekday:1,sectionType:1,startWeek:1,endWeek:18,capacity:50}) }
  dialog.value=true
}
async function submit(){
  if(!form.courseId||!form.teacherId||!form.classroomId) return ElMessage.warning('课程/教师/教室必填')
  const body:any={courseId:form.courseId, teacherId:Number(form.teacherId), classroomId:Number(form.classroomId), semester:semester.value, weekday:form.weekday, sectionType:String(form.sectionType), startWeek:form.startWeek, endWeek:form.endWeek, capacity:form.capacity, majorId:majorId.value}
  if(form.id) body.id=form.id
  await request.post('/scheduling/add', body)
  ElMessage.success('保存成功'); dialog.value=false; loadList()
}
async function remove(row:any){
  try{ await ElMessageBox.confirm('确认删除该排课记录？','删除',{type:'warning'}) }catch{ return }
  await request.post(`/scheduling/delete/${row.id}`); ElMessage.success('已删除'); loadList()
}
onMounted(async()=>{ await loadMeta(); })
</script>
