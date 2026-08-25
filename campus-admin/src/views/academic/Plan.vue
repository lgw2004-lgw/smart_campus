<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:10px">
      <h3>培养方案管理</h3>
      <div style="display:flex;gap:8px;align-items:center">
        <el-tree-select v-model="majorId" :data="deptTree" :props="{label:'dept_name',value:'dept_id',children:'children'}" placeholder="选择专业" check-strictly style="width:220px" @change="loadList"/>
        <el-tag type="success" effect="plain">总学分 {{ totalCredit }}</el-tag>
        <el-button type="warning" @click="openAdd">添加课程</el-button>
      </div>
    </div>
    <el-table :data="list" border v-loading="loading">
      <el-table-column prop="year_no" label="学年" width="70"><template #default="{row}">第{{ ['一','二','三','四'][row.year_no-1]||row.year_no }}年</template></el-table-column>
      <el-table-column prop="term" label="学期" width="70"><template #default="{row}">{{ row.term===1?'第一学期':'第二学期' }}</template></el-table-column>
      <el-table-column prop="course_id" label="课程" width="200"><template #default="{row}">{{ courseMap[row.course_id]||row.course_id }}</template></el-table-column>
      <el-table-column prop="credit" label="学分" width="70"/>
      <el-table-column prop="course_type" label="类型" width="120"><template #default="{row}">{{ courseTypeMap[row.course_type]||row.course_type }}</template></el-table-column>
      <el-table-column prop="is_required" label="性质" width="90"><template #default="{row}"><el-tag size="small" :type="row.is_required==='1'?'danger':'info'">{{ row.is_required==='1'?'必修':'选修' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="100"><template #default="{row}"><el-button size="small" type="danger" @click="remove(row)">删除</el-button></template></el-table-column>
    </el-table>

    <el-dialog v-model="dialog" title="添加培养方案课程" width="480">
      <el-form :model="form" label-width="90px">
        <el-form-item label="课程"><el-select v-model="form.courseId" filterable :filter-method="filterCourses" placeholder="默认显示本学院课程，输入编码可跨学院搜索" style="width:100%"><el-option v-for="c in displayCourses" :key="c.course_id" :label="`${c.course_name} (${c.course_code})`" :value="c.course_id"/></el-select></el-form-item>
        <el-form-item label="学年"><el-select v-model="form.yearNo" style="width:100%"><el-option :value="1" label="第一学年"/><el-option :value="2" label="第二学年"/><el-option :value="3" label="第三学年"/><el-option :value="4" label="第四学年"/></el-select></el-form-item>
        <el-form-item label="学期"><el-select v-model="form.term" style="width:100%"><el-option :value="1" label="第一学期"/><el-option :value="2" label="第二学期"/></el-select></el-form-item>
        <el-form-item label="性质"><el-select v-model="form.isRequired" style="width:100%"><el-option value="1" label="必修"/><el-option value="0" label="选修"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import request from '@/utils/request'
import { useDict } from '@/composables/useDict'
import { ElMessage, ElMessageBox } from 'element-plus'
const loading=ref(false)
const deptTree=ref<any[]>([])
const deptMap=ref<Record<number,number>>({})
const majorId=ref<number|null>(null)
const list=ref<any[]>([])
const courseTypeDict=useDict('course_type')
const courseTypeMap=computed(()=>{ const m:Record<string,string>={}; for(const d of courseTypeDict.value) m[d.dict_value]=d.dict_label; return m })
const courseMap=ref<Record<string,string>>({})
const courseOptions=ref<any[]>([])
const displayCourses=ref<any[]>([])
const totalCredit=computed(()=> list.value.reduce((s:number,r:any)=> s+Number(r.credit||0),0))
const collegeIdForMajor=computed(()=>{
  if(!majorId.value) return null
  const pid=deptMap.value[majorId.value]
  if(pid===0||pid===undefined) return majorId.value
  return pid
})
function refreshDisplayCourses(){
  const cid=collegeIdForMajor.value
  if(!cid) { displayCourses.value=[]; return }
  displayCourses.value=courseOptions.value.filter((c:any)=> c.dept_id==cid || c.dept_id==0)
}
function filterCourses(q:string){
  const cid=collegeIdForMajor.value
  if(!q){
    refreshDisplayCourses()
    return
  }
  const kw=q.toLowerCase()
  displayCourses.value=courseOptions.value.filter((c:any)=> (c.course_code && c.course_code.toLowerCase().includes(kw)) || (c.course_name && c.course_name.toLowerCase().includes(kw)))
}
watch(majorId, refreshDisplayCourses)
async function loadMeta(){
  const t:any=await request.get('/dept/tree'); deptTree.value=t.data||[]
  // build dept_id -> parent_id map
  const m:Record<number,number>={}
  const walk=(nodes:any[])=>{ for(const n of nodes){ m[n.dept_id]=n.parent_id; if(n.children) walk(n.children)} }
  walk(t.data||[]); deptMap.value=m
  const c:any=await request.post('/course/queryByPage',{pageNo:1,pageSize:2000,data:{}}); const cm:Record<string,string>={}; for(const x of (c.data.list||[])) cm[x.course_id]=x.course_name; courseMap.value=cm; courseOptions.value=c.data.list||[]; refreshDisplayCourses()
}
async function loadList(){
  if(!majorId.value) return
  if(deptMap.value[majorId.value]===0){
    ElMessage.warning('请选择具体专业，而非学院')
    list.value=[]
    return
  }
  loading.value=true
  try{ const r:any=await request.post('/plan/queryByMajor',{majorId:majorId.value}); list.value=r.data||[] }finally{ loading.value=false }
}
const dialog=ref(false)
const form=reactive<any>({courseId:'',yearNo:1,term:1,isRequired:'1'})
function openAdd(){
  if(!majorId.value) return ElMessage.warning('请先选择专业')
  if(deptMap.value[majorId.value]===0) return ElMessage.warning('请选择具体专业，而非学院')
  form.courseId=''; form.yearNo=1; form.term=1; form.isRequired='1'; dialog.value=true
}
async function submit(){
  if(!form.courseId) return ElMessage.warning('请选择课程')
  await request.post('/plan/save',{majorId:majorId.value, courseId:form.courseId, yearNo:form.yearNo, term:form.term, isRequired:form.isRequired})
  ElMessage.success('已添加'); dialog.value=false; loadList()
}
async function remove(row:any){
  try{ await ElMessageBox.confirm('确认删除该培养方案课程？','删除',{type:'warning'}) }catch{ return }
  await request.post(`/plan/delete/${row.plan_id}`); ElMessage.success('已删除'); loadList()
}
onMounted(loadMeta)
</script>
