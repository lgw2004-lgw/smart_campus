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
      <el-table-column prop="student_id" label="学号" width="170"/>
      <el-table-column prop="name" label="姓名" width="100"/>
      <el-table-column prop="sex" label="性别" width="70"><template #default="{row}">{{ row.sex==='1'?'女':'男' }}</template></el-table-column>
      <el-table-column prop="id_card" label="身份证" width="190"/>
      <el-table-column prop="phone" label="手机" width="130"/>
      <el-table-column label="院系/专业" width="180"><template #default="{row}">{{ deptMap[row.dept_id] || row.dept_id }}</template></el-table-column>
      <el-table-column prop="class_id" label="班级" width="100"><template #default="{row}">{{ classMap[row.class_id] || row.class_id }}</template></el-table-column>
      <el-table-column label="操作" width="320"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="warning" @click="openFile(row)">档案</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialog" :title="form.studentId?'编辑学生':'新生建档'" width="620">
      <el-form :model="form" label-width="90px">
        <el-form-item label="学号"><el-input v-model="form.studentId" :disabled="!!form._edit" placeholder="留空自动生成 STU"/></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="性别"><el-select v-model="form.sex"><el-option label="男" value="0"/><el-option label="女" value="1"/></el-select></el-form-item>
        <el-form-item label="身份证"><el-input v-model="form.idCard" @blur="onIdCardBlur"><template #append><el-button @click="checkIdCardByInput">回填查询</el-button></template></el-input></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone"/></el-form-item>
        <el-form-item label="专业"><el-tree-select v-model="form.deptId" :data="deptTree" :props="{label:'dept_name', value:'dept_id', children:'children'}" placeholder="选择专业（如 软件工程）" clearable check-strictly style="width:100%" /></el-form-item>
        <el-form-item label="班级"><el-select v-model="form.classId" placeholder="选择班级" clearable style="width:100%"><el-option v-for="c in classOptions" :key="c.class_id" :label="c.class_name" :value="c.class_id"/></el-select></el-form-item>
        <el-form-item label="入学年份"><el-input v-model="form.enrollYear" type="number" placeholder="2024"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="fileDialog" title="档案（家庭/健康/奖惩）" width="620">
      <el-form :model="fileForm" label-width="100px">
        <el-form-item label="家庭信息"><el-input type="textarea" v-model="fileForm.familyInfo" :rows="2"/></el-form-item>
        <el-form-item label="健康信息"><el-input type="textarea" v-model="fileForm.healthInfo" :rows="2"/></el-form-item>
        <el-form-item label="奖惩"><el-input type="textarea" v-model="fileForm.awardPunish" :rows="2"/></el-form-item>
        <el-form-item label="备注"><el-input v-model="fileForm.remark"/></el-form-item>
        <el-form-item label="紧急联系人"><el-input v-model="fileForm.emergencyContact"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="fileDialog=false">取消</el-button><el-button type="primary" @click="saveFile">保存档案</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/student/queryByPage', {name:''})
fetch()
const deptTree=ref<any[]>([])
const deptMap=ref<Record<string,string>>({})
const classOptions=ref<any[]>([])
const classMap=ref<Record<string,string>>({})
async function loadDepts(){ const res:any=await request.get('/dept/tree'); deptTree.value=res.data||[]; const m:Record<string,string>={}; const dfs=(arr:any[])=>{ for(const d of arr){ m[d.dept_id]=d.dept_name; if(d.children) dfs(d.children) } }; dfs(deptTree.value); deptMap.value=m }
async function loadClasses(){ const res:any=await request.post('/class/queryByPage', {pageNo:1,pageSize:50,data:{}}); const lst=res.data.list||[]; classOptions.value=lst; const m:Record<string,string>={}; for(const c of lst) m[c.class_id]=c.class_name; classMap.value=m }
onMounted(()=>{ loadDepts(); loadClasses() })
const dialog=ref(false)
const form=reactive<any>({studentId:'', name:'', sex:'0', idCard:'', phone:'', deptId:'', classId:'', enrollYear:'', _edit:false})
function openAdd(){ Object.assign(form,{studentId:'',name:'',sex:'0',idCard:'',phone:'',deptId:'',classId:'',enrollYear:'2024',_edit:false}); dialog.value=true }
function openEdit(row:any){ Object.assign(form,{studentId:row.student_id,name:row.name,sex:row.sex,idCard:row.id_card,phone:row.phone,deptId:row.dept_id,classId:row.class_id,enrollYear:row.enroll_year,_edit:true}); dialog.value=true }
async function submit(){ if(!form.name) return ElMessage.warning('姓名必填'); await request.post('/student/add', {studentId:form.studentId||undefined, name:form.name, sex:form.sex, idCard:form.idCard, phone:form.phone, deptId:form.deptId?Number(form.deptId):null, classId:form.classId?Number(form.classId):null, enrollYear:form.enrollYear?Number(form.enrollYear):null}); ElMessage.success('保存成功'); dialog.value=false; fetch() }
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除学生「${row.name}（${row.student_id}）」？将同时删除其选课/成绩/宿舍/借阅等关联数据`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/student/delete/${row.student_id}`)
  ElMessage.success('已删除'); fetch()
}
async function checkIdCard(row:any){ const res:any = await request.get('/student/queryByIdCard', {params:{idCard:row.id_card}}); ElMessage.success(`回填：${JSON.stringify(res.data).slice(0,80)}`) }
async function checkIdCardByInput(){ if(!form.idCard) return; const res:any = await request.get('/student/queryByIdCard', {params:{idCard:form.idCard}}); if(res.data) { form.name=res.data.name; form.phone=res.data.phone } }
function onIdCardBlur(){ if(form.idCard && form.idCard.length===18) checkIdCardByInput() }

// 档案
const fileDialog=ref(false)
const fileForm=reactive<any>({studentId:'', familyInfo:'', healthInfo:'', awardPunish:'', remark:'', emergencyContact:''})
let curStuId=''
async function openFile(row:any){
  curStuId=row.student_id
  const res:any = await request.get(`/studentFile/queryById/${curStuId}`)
  const d=res.data||{}
  fileForm.studentId=curStuId; fileForm.familyInfo=d.family_info||''; fileForm.healthInfo=d.health_info||''; fileForm.awardPunish=d.award_punish||''; fileForm.remark=d.remark||''; fileForm.emergencyContact=d.emergency_contact||''; fileDialog.value=true
}
async function saveFile(){
  await request.put('/studentFile/add', {studentId:curStuId, familyInfo:fileForm.familyInfo, healthInfo:fileForm.healthInfo, awardPunish:fileForm.awardPunish, remark:fileForm.remark, emergencyContact:fileForm.emergencyContact})
  ElMessage.success('档案已保存'); fileDialog.value=false
}
</script>
