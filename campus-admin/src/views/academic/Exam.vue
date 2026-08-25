<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>考试管理 · 管理员可发布全校考试，各学院教务仅能发布本院课程考试</h3>
      <div>
        <el-select v-model="query.semester" placeholder="学期" clearable style="width:150px;margin-right:6px"><el-option v-for="s in semesterOptions" :key="s" :label="s" :value="s"/></el-select>
        <el-select v-model="query.examType" placeholder="类型" clearable style="width:120px;margin-right:6px"><el-option label="期中" value="0"/><el-option label="期末" value="1"/><el-option label="补考" value="2"/><el-option label="重修" value="3"/></el-select>
        <el-select v-model="query.status" placeholder="状态" clearable style="width:120px;margin-right:6px"><el-option label="未发布" value="0"/><el-option label="已发布" value="1"/></el-select>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openAdd()">新增考试</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="exam_id" label="考试ID" width="150"/>
      <el-table-column label="考试名称" min-width="160"><template #default="{row}">{{ row.exam_name }}</template></el-table-column>
      <el-table-column label="课程" min-width="150"><template #default="{row}">{{ courseMap[row.course_id] || row.course_id }}</template></el-table-column>
      <el-table-column label="类型" width="80"><template #default="{row}"><el-tag size="small">{{ examTypeMap[row.exam_type] }}</el-tag></template></el-table-column>
      <el-table-column prop="semester" label="学期" width="120"/>
      <el-table-column label="考试日期" width="110"><template #default="{row}">{{ row.exam_date }}</template></el-table-column>
      <el-table-column label="时间" width="130"><template #default="{row}">{{ row.start_time }}~{{ row.end_time }}</template></el-table-column>
      <el-table-column label="教室" width="100"><template #default="{row}">{{ row.room_no || '—' }}</template></el-table-column>
      <el-table-column label="状态" width="90"><template #default="{row}"><el-tag :type="row.status==='1'?'success':'info'" size="small">{{ row.status==='1'?'已发布':'未发布' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" :type="row.status==='1'?'warning':'success'" @click="togglePublish(row)">{{ row.status==='1'?'撤回':'发布' }}</el-button>
          <el-button size="small" type="danger" @click="removeRow(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialog" :title="isEdit?'编辑考试':'新增考试'" width="620">
      <el-form :model="form" label-width="90px">
        <el-form-item label="课程">
          <el-select v-model="form.courseId" filterable style="width:100%" :disabled="isEdit" @change="onCourseChange">
            <el-option v-for="c in courseList" :key="c.course_id" :label="c.course_name + ' (' + (collegeMap[c.dept_id]||c.dept_id) + ')'" :value="c.course_id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="考试名称"><el-input v-model="form.examName" placeholder="如：高等数学(上) 期末"/></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.examType" style="width:100%"><el-option label="期中" value="0"/><el-option label="期末" value="1"/><el-option label="补考" value="2"/><el-option label="重修" value="3"/></el-select>
        </el-form-item>
        <el-form-item label="学期"><el-select v-model="form.semester" filterable allow-create style="width:100%"><el-option v-for="s in semesterOptions" :key="s" :label="s" :value="s"/></el-select></el-form-item>
        <el-form-item label="考试日期"><el-date-picker v-model="form.examDate" type="date" value-format="YYYY-MM-DD" style="width:100%"/></el-form-item>
        <el-form-item label="开始时间"><el-time-picker v-model="form.startTime" value-format="HH:mm:ss" format="HH:mm" style="width:100%"/></el-form-item>
        <el-form-item label="结束时间"><el-time-picker v-model="form.endTime" value-format="HH:mm:ss" format="HH:mm" style="width:100%"/></el-form-item>
        <el-form-item label="教室">
          <el-select v-model="form.classroomId" filterable style="width:100%" @change="onRoomChange">
            <el-option v-for="r in roomList" :key="r.classroom_id" :label="r.room_no + ' (容量' + r.capacity + ')'" :value="r.classroom_id"/>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
const auth = useAuthStore()
const isAdmin = auth.userType === '1' || auth.userType === '0'
const isJwc = auth.userType === '6'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/exam/queryByPage', { semester:'', examType:'', status:'' })
fetch()
const courseMap = ref<Record<string,string>>({})
const collegeMap = ref<Record<number,string>>({})
const courseList = ref<any[]>([])
const roomList = ref<any[]>([])
const examTypeMap:Record<string,string> = { '0':'期中', '1':'期末', '2':'补考', '3':'重修' }
const semesterOptions = ref<string[]>(['2024-2025-1','2024-2025-2','2025-2026-1','2025-2026-2'])
async function loadCourses(){
  const res:any = await request.post('/course/queryByPage', { pageNo:1, pageSize:500, data:{} })
  courseList.value = res.data.list || []
  const m:Record<string,string> = {}; const cm:Record<number,string> = {}
  for(const c of courseList.value) m[c.course_id] = c.course_name
  courseMap.value = m
  const res2:any = await request.post('/dept/queryByPage', { pageNo:1, pageSize:100, data:{} })
  for(const d of (res2.data.list||[])) cm[d.dept_id] = d.dept_name
  collegeMap.value = cm
}
async function loadRooms(){
  try{
    const res:any = await request.post('/classroom/queryByPage', { pageNo:1, pageSize:2000, data:{} })
    roomList.value = res.data.list || []
  }catch{}
}
onMounted(()=>{ loadCourses(); loadRooms() })
const dialog = ref(false); const isEdit = ref(false)
const form = reactive<any>({ examId:'', courseId:'', examName:'', examType:'1', semester:'2024-2025-1', examDate:'', startTime:'', endTime:'', classroomId:'', roomNo:'' })
function onCourseChange(){ const c = courseList.value.find(x=>x.course_id===form.courseId); form.examName = c? c.course_name + ' 考试' : form.examName }
function onRoomChange(){ const r = roomList.value.find(x=>x.classroom_id===form.classroomId); form.roomNo = r? r.room_no : '' }
function openAdd(){ isEdit.value=false; Object.assign(form,{examId:'',courseId:'',examName:'',examType:'1',semester:'2024-2025-1',examDate:'',startTime:'',endTime:'',classroomId:'',roomNo:''}); dialog.value=true }
function openEdit(row:any){ isEdit.value=true; Object.assign(form,{examId:row.exam_id,courseId:row.course_id,examName:row.exam_name,examType:row.exam_type,semester:row.semester,examDate:row.exam_date,startTime:row.start_time,endTime:row.end_time,classroomId:row.classroom_id,roomNo:row.room_no}); dialog.value=true }
async function submit(){
  if(!form.courseId) return ElMessage.warning('请选择课程')
  await request.post('/exam/save', { examId:form.examId||undefined, courseId:form.courseId, examName:form.examName, examType:form.examType, semester:form.semester, examDate:form.examDate, startTime:form.startTime, endTime:form.endTime, classroomId:form.classroomId||null, roomNo:form.roomNo||null })
  ElMessage.success('已保存'); dialog.value=false; fetch()
}
async function togglePublish(row:any){
  const status = row.status==='1'?'0':'1'
  try{ await request.post('/exam/publish', { examId:row.exam_id, status }); ElMessage.success(status==='1'?'已发布':'已撤回'); fetch() }
  catch(e:any){}
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除考试「${row.exam_name}」？`,'删除',{type:'warning'}) }catch{ return }
  try{ await request.post(`/exam/delete/${row.exam_id}`); ElMessage.success('已删除'); fetch() }catch(e:any){}
}
</script>
