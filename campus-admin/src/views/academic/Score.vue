<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>成绩管理 · 逐级上报：教师填写→教务确认→管理员终审（提交后逐级锁定）</h3>
      <div>
        <el-input v-model="query.studentId" placeholder="学号" clearable style="width:130px;margin-right:6px"/>
        <el-select v-model="query.courseId" placeholder="课程" clearable filterable style="width:160px;margin-right:6px"><el-option v-for="(name,id) in courseMap" :key="id" :label="name" :value="id"/></el-select>
        <el-select v-model="query.status" placeholder="状态" clearable style="width:130px;margin-right:6px">
          <el-option label="教师草稿" value="0"/><el-option label="待教务确认" value="1"/><el-option label="待管理员终审" value="2"/><el-option label="已终审" value="3"/>
        </el-select>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openAdd()">录入成绩</el-button>
        <el-button v-if="isAdmin||isJwc" type="warning" @click="showRank">统计</el-button>
      </div>
    </div>
    <el-upload v-if="isAdmin||isJwc" :action="uploadUrl" :headers="headers" :show-file-list="false" :on-success="onUploadSuccess" :on-error="onUploadError" accept=".xlsx,.xls" style="margin-bottom:10px">
      <el-button size="small" type="info">Excel导入（列：学号,课程ID,分数,学期）</el-button>
    </el-upload>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="score_id" label="ID" width="160"/>
      <el-table-column prop="student_id" label="学号" width="110"/>
      <el-table-column label="课程" width="150"><template #default="{row}">{{ courseMap[row.course_id] || row.course_id }}</template></el-table-column>
      <el-table-column prop="score" label="分数" width="80"/>
      <el-table-column prop="gpa_point" label="绩点" width="80"><template #default="{row}"><el-tag size="small" type="info">{{ row.gpa_point }}</el-tag></template></el-table-column>
      <el-table-column prop="semester" label="学期" width="120"/>
      <el-table-column label="状态" width="120"><template #default="{row}"><el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{row}">
          <el-button size="small" :disabled="!canEdit(row)" @click="openEdit(row)">编辑</el-button>
          <el-button v-if="(isTeacher||isAdmin) && row.status==='0'" size="small" type="primary" @click="doSubmit(row,'teacher_submit')">提交</el-button>
          <el-button v-if="(isJwc||isAdmin) && row.status==='1'" size="small" type="success" @click="doSubmit(row,'jwc_confirm')">教务确认</el-button>
          <el-button v-if="(isJwc||isAdmin) && (row.status==='1'||row.status==='2')" size="small" type="warning" @click="doSubmit(row,'jwc_reject')">退回</el-button>
          <el-button v-if="isAdmin && row.status==='2'" size="small" type="success" @click="doSubmit(row,'admin_finalize')">管理员终审</el-button>
          <el-button v-if="isAdmin && row.status==='3'" size="small" type="danger" @click="doSubmit(row,'admin_reopen')">重开</el-button>
          <el-button v-if="isAdmin||isJwc" size="small" type="danger" @click="removeRow(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialog" :title="isEdit?'修改成绩（仅分数可改）':'录入成绩'" width="520">
      <el-form :model="form" label-width="80px">
        <el-form-item label="学号"><el-input v-model="form.studentId" :disabled="isEdit||isJwc"/></el-form-item>
        <el-form-item label="课程"><el-select v-model="form.courseId" filterable style="width:100%" :disabled="isEdit||isJwc"><el-option v-for="(name,id) in courseMap" :key="id" :label="name" :value="id"/></el-select></el-form-item>
        <el-form-item label="分数"><el-input-number v-model="form.score" :min="0" :max="100" @change="calcGpa" /> <span style="margin-left:12px;color:#8a94a6">绩点 <el-tag size="small">{{ gpaPreview }}</el-tag> 自动计算</span></el-form-item>
        <el-form-item label="学期"><el-input v-model="form.semester" placeholder="2024-2025-1" :disabled="isEdit||isJwc"/></el-form-item>
        <el-form-item label="考试ID"><el-input v-model="form.examId" placeholder="可选" :disabled="isEdit||isJwc"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">{{ isEdit?'保存修改':'保存' }}</el-button></template>
    </el-dialog>

    <el-dialog v-model="rankDialog" title="成绩分布" width="520">
      <div v-if="rankData">
        <div>平均分：{{ rankData.avg }} 总数：{{ rankData.total }}</div>
        <div style="margin-top:8px" v-for="(v,k) in rankData.buckets" :key="k">{{ k }}：{{ v }}人</div>
      </div>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
const auth = useAuthStore()
const ut = auth.userType
const isAdmin = ut === '1' || ut === '0'
const isJwc = ut === '6'
const isTeacher = ut === '7'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/score/queryByPage', {studentId:'', courseId:'', status:''})
fetch()
const courseMap=ref<Record<string,string>>({})
async function loadCourseMap(){ const res:any=await request.post('/course/queryByPage', {pageNo:1,pageSize:500,data:{}}); const m:Record<string,string>={}; for(const c of (res.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }
onMounted(loadCourseMap)
function statusText(s:string){ return {'0':'教师草稿','1':'待教务确认','2':'待管理员终审','3':'已终审'}[s] || '未知' }
function statusType(s:string){ return {'0':'info','1':'warning','2':'primary','3':'success'}[s] || 'info' }
function canEdit(row:any){
  if(isAdmin) return true
  if(isJwc) return row.status==='0' || row.status==='1'
  if(isTeacher) return row.status==='0'
  return false
}
const dialog=ref(false)
const isEdit=ref(false)
const form=reactive<any>({studentId:'', courseId:'', score:60, semester:'2024-2025-1', examId:''})
const gpaPreview=ref('1.00')
function calcGpa(){ const s=Number(form.score); let g=0; if(s>=90) g=4.0; else if(s>=80) g=3.0; else if(s>=70) g=2.0; else if(s>=60) g=1.0; else g=0; gpaPreview.value=g.toFixed(2) }
function openAdd(){ isEdit.value=false; form.studentId=''; form.courseId=''; form.score=60; form.semester='2024-2025-1'; form.examId=''; calcGpa(); dialog.value=true }
function openEdit(row:any){ isEdit.value=true; form.studentId=row.student_id; form.courseId=row.course_id; form.score=Number(row.score); form.semester=row.semester; form.examId=row.exam_id||''; calcGpa(); dialog.value=true }
async function submit(){ if(!form.studentId||!form.courseId) return ElMessage.warning('必填'); await request.post('/score/add', {studentId:form.studentId, courseId:form.courseId, score:form.score, semester:form.semester, examId:form.examId||null}); ElMessage.success(isEdit.value?'修改成功，绩点已自动重算':'已保存（草稿）'); dialog.value=false; fetch() }
async function doSubmit(row:any, action:string){
  const msg = {'teacher_submit':'提交后教师不可再修改，确认提交？','jwc_confirm':'确认后将上报管理员终审，确认提交？','jwc_reject':'确认退回教师重新填写？','admin_finalize':'终审后仅管理员可修改，确认？','admin_reopen':'确认重开为草稿？'}[action]||'确认？'
  try{ await ElMessageBox.confirm(msg,'提示',{type:'warning'}) }catch{ return }
  try{ await request.post('/score/submit', {scoreId:row.score_id, action}); ElMessage.success('操作成功'); fetch() }catch(e:any){}
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除该成绩记录（${courseMap.value[row.course_id]||row.course_id} ${row.score}分）？`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/score/delete/${row.score_id}`)
  ElMessage.success('已删除'); fetch()
}
const token=localStorage.getItem('token')||''
const headers=computed(()=>({token}))
const uploadUrl='/score/import'
function onUploadSuccess(res:any){ if(res.code===200) { ElMessage.success(`导入${res.data.imported}条`); fetch() } else ElMessage.error(res.message) }
function onUploadError(){ ElMessage.error('导入失败') }
const rankDialog=ref(false); const rankData=ref<any>(null)
async function showRank(){ const res:any = await request.post('/score/queryRank', {courseId:query.courseId||undefined}); rankData.value=res.data; rankDialog.value=true }
</script>
