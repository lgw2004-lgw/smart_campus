<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>排课管理 · 周视图 7天×4节（1-2/3-4/5-6/7-8）</h3>
      <div>
        <el-date-picker v-model="weekStart" type="date" placeholder="选择周一" :disabled-date="(d:any)=>false" @change="loadWeek" style="margin-right:8px"/>
        <el-button @click="prevWeek">上一周</el-button>
        <el-button @click="nextWeek">下一周</el-button>
      </div>
    </div>
    <el-table :data="rows" border v-loading="loading" style="width:100%">
      <el-table-column label="节次" width="120"><template #default="{row}">{{ sectionLabel(row.section) }}</template></el-table-column>
      <el-table-column v-for="day in days" :key="day.value" :label="day.label" min-width="140">
        <template #default="{row}">
          <div v-if="cellKey(row.section, day.date) && map[cellKey(row.section, day.date)]" style="background:#e6f7ff;padding:6px;border-radius:6px">
            <div style="font-weight:bold">{{ map[cellKey(row.section, day.date)].course_id }}</div>
            <div style="font-size:12px;color:#666">教师:{{ map[cellKey(row.section, day.date)].teacher_id }} 教室:{{ map[cellKey(row.section, day.date)].classroom_id }}</div>
            <el-tag v-if="map[cellKey(row.section, day.date)].scheduling_type==='0'" type="danger" size="small">停课</el-tag>
            <div style="margin-top:4px;display:flex;gap:4px">
              <el-button size="small" @click="openEdit(map[cellKey(row.section, day.date)], day.date, row.section)">编辑</el-button>
              <el-button size="small" type="danger" @click="removeRow(map[cellKey(row.section, day.date)])">删除</el-button>
            </div>
          </div>
          <div v-else>
            <el-button size="small" type="primary" plain @click="openEdit(null, day.date, row.section)">排课</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialog" title="排课编辑" width="520">
      <el-form :model="form" label-width="90px">
        <el-form-item label="日期"><el-input :value="form.schedulingDay" disabled/></el-form-item>
        <el-form-item label="节次"><el-select v-model="form.sectionType" disabled><el-option label="1-2节" value="1"/><el-option label="3-4节" value="2"/><el-option label="5-6节" value="3"/><el-option label="7-8节" value="4"/></el-select></el-form-item>
        <el-form-item label="课程ID"><el-input v-model="form.courseId" placeholder="COUR..." /></el-form-item>
        <el-form-item label="教师ID"><el-input v-model="form.teacherId" type="number" /></el-form-item>
        <el-form-item label="教室ID"><el-input v-model="form.classroomId" type="number" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.schedulingType"><el-option label="有课" value="1"/><el-option label="停课" value="0"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const weekStart = ref<Date>(getMonday(new Date()))
const loading = ref(false)
const rows = [{section:'1'},{section:'2'},{section:'3'},{section:'4'}]
function sectionLabel(s:string){ return s==='1'?'1-2节':s==='2'?'3-4节':s==='3'?'5-6节':'7-8节' }
function getMonday(d:Date){ const t=new Date(d); const day=t.getDay(); const diff=t.getDate()-day+(day===0?-6:1); t.setDate(diff); t.setHours(0,0,0,0); return t }
function format(d:Date){ return d.toISOString().slice(0,10) }
const days = computed(()=>{
  const arr=[]; for(let i=0;i<7;i++){ const dt=new Date(weekStart.value); dt.setDate(weekStart.value.getDate()+i); arr.push({label:`${['周一','周二','周三','周四','周五','周六','周日'][i]} ${format(dt)}`, value:i, date:format(dt)}) } return arr
})
function cellKey(section:string, date:string){ return `${date}__${section}` }
const map = ref<Record<string,any>>({})
async function loadWeek(){
  loading.value=true
  try{
    const start=format(weekStart.value); const end=new Date(weekStart.value); end.setDate(weekStart.value.getDate()+6); const endStr=format(end)
    const res:any = await request.post('/scheduling/selectWithConditions', {})
    const list=res?.data ?? []
    const m:Record<string,any>={}
    for(const r of list){
      if(r.scheduling_day>=start && r.scheduling_day<=endStr){
        m[`${r.scheduling_day}__${r.section_type}`]=r
      }
    }
    map.value=m
  }finally{ loading.value=false }
}
function prevWeek(){ const d=new Date(weekStart.value); d.setDate(d.getDate()-7); weekStart.value=d; loadWeek() }
function nextWeek(){ const d=new Date(weekStart.value); d.setDate(d.getDate()+7); weekStart.value=d; loadWeek() }
const dialog=ref(false)
const form=reactive<any>({id:null, courseId:'', teacherId:'', classroomId:'', schedulingDay:'', sectionType:'', schedulingType:'1'})
function openEdit(row:any|null, date:string, section:string){
  form.id=row?.id||null; form.courseId=row?.course_id||''; form.teacherId=row?.teacher_id||''; form.classroomId=row?.classroom_id||''; form.schedulingDay=date; form.sectionType=section; form.schedulingType=row?.scheduling_type||'1'; dialog.value=true
}
async function submit(){
  if(!form.courseId||!form.teacherId||!form.classroomId) return ElMessage.warning('课程/教师/教室必填')
  if(form.id){
    await request.post('/scheduling/update', {id:form.id, courseId:form.courseId, teacherId:Number(form.teacherId), classroomId:Number(form.classroomId), schedulingDay:form.schedulingDay, sectionType:form.sectionType, schedulingType:form.schedulingType})
  }else{
    await request.post('/scheduling/add', {courseId:form.courseId, teacherId:Number(form.teacherId), classroomId:Number(form.classroomId), schedulingDay:form.schedulingDay, sectionType:form.sectionType, schedulingType:form.schedulingType})
  }
  ElMessage.success('保存成功'); dialog.value=false; loadWeek()
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm('确认删除该排课记录？', '删除', {type:'warning'}) } catch{ return }
  await request.post(`/scheduling/delete/${row.id}`)
  ElMessage.success('已删除'); loadWeek()
}
loadWeek()
</script>
