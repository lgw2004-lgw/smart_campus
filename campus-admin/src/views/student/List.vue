<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>学生档案</h3>
      <div>
        <el-input v-model="query.name" placeholder="姓名" clearable style="width:140px;margin-right:6px"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openAdd()">新生建档</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="student_id" label="学号" width="150"/>
      <el-table-column prop="name" label="姓名" width="90"/>
      <el-table-column prop="sex" label="性别" width="60"><template #default="{row}">{{ row.sex==='1'?'女':'男' }}</template></el-table-column>
      <el-table-column prop="id_card" label="身份证" width="180"/>
      <el-table-column prop="phone" label="手机" width="120"/>
      <el-table-column label="学院" width="150"><template #default="{row}">{{ getStudentCollege(row) }}</template></el-table-column>
      <el-table-column label="专业" width="150"><template #default="{row}">{{ getStudentMajor(row) }}</template></el-table-column>
      <el-table-column prop="class_id" label="班级" width="130"><template #default="{row}">{{ classMap[row.class_id] || (row.class_id||'-') }}</template></el-table-column>
      <el-table-column label="操作" width="300"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="warning" @click="openFile(row)">档案</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialog" :title="form.studentId?'编辑学生':'新生建档'" width="620">
      <el-form :model="form" label-width="90px">
        <el-form-item label="学号"><el-input v-model="form.studentId" :disabled="!!form._edit" placeholder="留空自动生成 STU"/></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="性别"><el-select v-model="form.sex"><el-option label="男" value="0"/><el-option label="女" value="1"/></el-select></el-form-item>
        <el-form-item label="身份证"><el-input v-model="form.idCard" @blur="onIdCardBlur"><template #append><el-button @click="checkIdCardByInput">回填查询</el-button></template></el-input></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone"/></el-form-item>
        <el-form-item label="学院"><el-input :model-value="derivedCollegeName" disabled placeholder="选择班级后自动带出" /></el-form-item>
        <el-form-item label="专业"><el-input :model-value="derivedMajorName" disabled placeholder="选择班级后自动带出" /></el-form-item>
        <el-form-item label="班级"><el-select v-model="form.classId" placeholder="选择班级（决定学院/专业）" clearable style="width:100%"><el-option v-for="c in classOptions" :key="c.class_id" :label="`${c.class_name} — ${deptMap[c.dept_id]||'未绑定专业'}`" :value="c.class_id"/></el-select></el-form-item>
        <el-form-item label="入学年份"><el-input v-model="form.enrollYear" type="number" placeholder="2024"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="fileDialog" title="档案（家庭/健康/奖惩）" width="680">
      <el-form :model="fileForm" label-width="100px">
        <el-form-item label="家庭信息">
          <div style="width:100%">
            <div v-for="(m, idx) in fileForm.familyMembers" :key="idx" style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
              <el-input v-model="m.member" placeholder="家庭成员：如 张父" style="flex:1"/>
              <el-input v-model="m.relation" placeholder="关系：如 父子" style="flex:1"/>
              <el-button size="small" type="danger" @click="removeFamilyMember(idx)" :disabled="fileForm.familyMembers.length===1">删除</el-button>
            </div>
            <el-button size="small" type="primary" plain @click="addFamilyMember">+ 添加家庭成员</el-button>
          </div>
        </el-form-item>
        <el-form-item label="健康信息"><el-input type="textarea" v-model="fileForm.healthInfo" :rows="2"/></el-form-item>
        <el-form-item label="奖惩"><el-input type="textarea" v-model="fileForm.awardPunish" :rows="2"/></el-form-item>
        <el-form-item label="备注"><el-input v-model="fileForm.remark"/></el-form-item>
        <el-form-item label="紧急联系人">
          <div style="display:flex;gap:8px;width:100%">
            <el-input v-model="fileForm.emergencyContact" placeholder="联系人：如 张父" style="flex:1"/>
            <el-input v-model="fileForm.emergencyPhone" placeholder="电话：如 13800001234" style="flex:1"/>
          </div>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="fileDialog=false">取消</el-button><el-button type="primary" @click="saveFile">保存档案</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/student/queryByPage', {name:''})
fetch()
const deptTree=ref<any[]>([])
const deptMap=ref<Record<string,string>>({})
const parentMap=ref<Record<string,number>>({})
const classOptions=ref<any[]>([])
const classMap=ref<Record<string,string>>({})
const classDeptMap=ref<Record<string,number>>({})
async function loadDepts(){
  const res:any=await request.get('/dept/tree')
  deptTree.value=res.data||[]
  const m:Record<string,string>={}
  const pm:Record<string,number>={}
  const dfs=(arr:any[])=>{ for(const d of arr){ m[d.dept_id]=d.dept_name; pm[d.dept_id]=d.parent_id; if(d.children) dfs(d.children) } }
  dfs(deptTree.value)
  deptMap.value=m; parentMap.value=pm
}
async function loadClasses(){
  const res:any=await request.post('/class/queryByPage', {pageNo:1,pageSize:500,data:{}})
  const lst=res.data.list||[]
  classOptions.value=lst
  const m:Record<string,string>={}
  const dm:Record<string,number>={}
  for(const c of lst){ m[c.class_id]=c.class_name; dm[c.class_id]=c.dept_id }
  classMap.value=m; classDeptMap.value=dm
}
onMounted(()=>{ loadDepts(); loadClasses() })

function resolveDept(deptId:any){
  if(!deptId) return { college:'-', major:'-' }
  const pid=parentMap.value[deptId]
  if(pid===0) return { college: deptMap.value[deptId]||String(deptId), major:'-' }
  if(pid) return { college: deptMap.value[pid]||'-', major: deptMap.value[deptId]||String(deptId) }
  return { college:'-', major: deptMap.value[deptId]||String(deptId) }
}
function getStudentCollege(row:any){
  const deptId = (row.class_id && classDeptMap.value[row.class_id]) || row.dept_id
  return resolveDept(deptId).college
}
function getStudentMajor(row:any){
  const deptId = (row.class_id && classDeptMap.value[row.class_id]) || row.dept_id
  return resolveDept(deptId).major
}

const dialog=ref(false)
const form=reactive<any>({studentId:'', name:'', sex:'0', idCard:'', phone:'', classId:'', enrollYear:'', _edit:false})
const derivedDeptId = computed(()=> {
  if(!form.classId) return null
  return classDeptMap.value[form.classId] || null
})
const derivedCollegeName = computed(()=> {
  const d=derivedDeptId.value
  if(!d) return ''
  return resolveDept(d).college
})
const derivedMajorName = computed(()=> {
  const d=derivedDeptId.value
  if(!d) return ''
  return resolveDept(d).major
})

function openAdd(){ Object.assign(form,{studentId:'',name:'',sex:'0',idCard:'',phone:'',classId:'',enrollYear:'2024',_edit:false}); dialog.value=true }
function openEdit(row:any){
  Object.assign(form,{studentId:row.student_id,name:row.name,sex:row.sex,idCard:row.id_card,phone:row.phone,classId:row.class_id,enrollYear:row.enroll_year,_edit:true}); dialog.value=true
}
async function submit(){
  if(!form.name) return ElMessage.warning('姓名必填')
  if(!form.classId) return ElMessage.warning('请选择班级（学院/专业由班级决定）')
  const deptId = classDeptMap.value[form.classId]
  if(!deptId) return ElMessage.warning('该班级未绑定专业，请先在班级管理中设置所属专业')
  await request.post('/student/add', {studentId:form.studentId||undefined, name:form.name, sex:form.sex, idCard:form.idCard, phone:form.phone, deptId:Number(deptId), classId:Number(form.classId), enrollYear:form.enrollYear?Number(form.enrollYear):null}); ElMessage.success('保存成功'); dialog.value=false; fetch()
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除学生「${row.name}（${row.student_id}）」？将同时删除其选课/成绩/宿舍/借阅等关联数据`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/student/delete/${row.student_id}`)
  ElMessage.success('已删除'); fetch()
}
async function checkIdCardByInput(){ if(!form.idCard) return; const res:any = await request.get('/student/queryByIdCard', {params:{idCard:form.idCard}}); if(res.data) { form.name=res.data.name; form.phone=res.data.phone } }
function onIdCardBlur(){ if(form.idCard && form.idCard.length===18) checkIdCardByInput() }

// 档案
const fileDialog=ref(false)
const fileForm=reactive<any>({studentId:'', familyMembers:[{member:'', relation:''}], healthInfo:'', awardPunish:'', remark:'', emergencyContact:'', emergencyPhone:''})
let curStuId=''
function addFamilyMember(){ fileForm.familyMembers.push({member:'', relation:''}) }
function removeFamilyMember(idx:number){ if(fileForm.familyMembers.length>1) fileForm.familyMembers.splice(idx,1) }
function parseFamilyInfo(raw:string){
  if(!raw) return [{member:'', relation:''}]
  try{
    const arr=JSON.parse(raw)
    if(Array.isArray(arr) && arr.length) return arr.map((x:any)=> ({member: x.member||x.name||'', relation: x.relation||''}))
  }catch{}
  // 旧文本：整段作为一个成员名
  return [{member: raw, relation:''}]
}
async function openFile(row:any){
  curStuId=row.student_id
  const res:any = await request.get(`/studentFile/queryById/${curStuId}`)
  const d=res.data||{}
  fileForm.studentId=curStuId
  fileForm.familyMembers=parseFamilyInfo(d.family_info||'')
  fileForm.healthInfo=d.health_info||''; fileForm.awardPunish=d.award_punish||''; fileForm.remark=d.remark||''; fileForm.emergencyContact=d.emergency_contact||''; fileForm.emergencyPhone=d.emergency_phone||''; fileDialog.value=true
}
async function saveFile(){
  const clean=fileForm.familyMembers.filter((m:any)=> m.member.trim()||m.relation.trim())
  const familyInfo = clean.length? JSON.stringify(clean) : ''
  await request.put('/studentFile/add', {studentId:curStuId, familyInfo, healthInfo:fileForm.healthInfo, awardPunish:fileForm.awardPunish, remark:fileForm.remark, emergencyContact:fileForm.emergencyContact, emergencyPhone:fileForm.emergencyPhone})
  ElMessage.success('档案已保存'); fileDialog.value=false
}
</script>
