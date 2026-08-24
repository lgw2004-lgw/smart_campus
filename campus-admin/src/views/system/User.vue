<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
      <h3>用户管理 · user.vue → /user/insertOrUpdate → /user/save 分配角色</h3>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <el-input v-model="query.userName" placeholder="用户名" clearable style="width:140px"/>
        <el-select v-model="query.userType" placeholder="类型" clearable style="width:140px"><el-option v-for="o in typeOptions" :key="o.value" :label="o.label" :value="o.value"/></el-select>
        <el-tree-select v-model="query.deptId" :data="deptTree" :props="{label:'dept_name', value:'dept_id', children:'children'}" placeholder="院系" clearable check-strictly style="width:200px" />
        <el-button type="primary" @click="search">查询</el-button><el-button type="success" @click="openEdit()">新增用户</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="user_id" label="ID" width="70"/>
      <el-table-column prop="work_no" label="工号" width="110"/>
      <el-table-column prop="user_name" label="用户名" width="120"/>
      <el-table-column prop="phone" label="手机" width="130"/>
      <el-table-column prop="user_type" label="类型" width="100"><template #default="{row}">{{ typeMap[row.user_type] || row.user_type }}</template></el-table-column>
      <el-table-column label="院系" width="160"><template #default="{row}">{{ deptMap[row.dept_id] || (row.dept_id||'—') }}</template></el-table-column>
      <el-table-column prop="status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='0'?'success':'danger'">{{ row.status==='0'?'正常':'停用' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="260"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="warning" @click="openRole(row)">分配角色</el-button><el-button size="small" type="danger" @click="del(row)">停用</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialog" :title="form.userId?'编辑用户':'新增用户'" width="520">
      <el-form :model="form" label-width="80px">
        <el-form-item label="工号">
          <el-input v-model="form.workNo" :disabled="isSuperAdmin" :placeholder="isSuperAdmin?'0（超级管理员定死）': form.userType==='6'?'自动生成 0001…' : '自动生成 学院0001+序号00001，如 000100001'"/>
          <div v-if="!isSuperAdmin" style="font-size:12px;color:#8a94a6;margin-top:4px">留空则按“{{ workNoRuleTip }}”自动生成</div>
        </el-form-item>
        <el-form-item label="用户名"><el-input v-model="form.userName"/></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone"/></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" placeholder="留空不改，默认123456" show-password/></el-form-item>
        <el-form-item label="院系"><el-tree-select v-model="form.deptId" :data="deptTree" :props="{label:'dept_name', value:'dept_id', children:'children'}" :placeholder="isSuperAdmin?'超级管理员不属于任何院系': '选择院系（顶级为学院）'" clearable check-strictly :disabled="isSuperAdmin" style="width:100%" /></el-form-item>
        <el-form-item label="类型"><el-select v-model="form.userType" placeholder="随角色管理联动"><el-option v-for="r in typeOptions" :key="r.value" :label="r.label" :value="r.value"/></el-select></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="正常" value="0"/><el-option label="停用" value="1"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="roleDialog" title="分配角色" width="420">
      <el-checkbox-group v-model="roleIds">
        <el-checkbox v-for="r in roles" :key="r.role_id" :label="r.role_id">{{ r.role_name }}({{ r.role_code }})</el-checkbox>
      </el-checkbox-group>
      <template #footer><el-button @click="roleDialog=false">取消</el-button><el-button type="primary" @click="saveRole">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/user/queryByPage', {userName:'', userType:'', deptId:''} as any)
fetch()
const deptTree=ref<any[]>([])
const deptMap=ref<Record<string,string>>({})
const typeOptions=ref<any[]>([{label:'管理员',value:'0'},{label:'教师',value:'1'},{label:'学生',value:'2'}])
const typeMap=ref<Record<string,string>>({'0':'管理员','1':'教师','2':'学生'})
async function loadDepts(){
  const res:any=await request.get('/dept/tree'); deptTree.value=res.data||[]
  const m:Record<string,string>={}
  const dfs=(arr:any[])=>{ for(const d of arr){ m[d.dept_id]=d.dept_name; if(d.children) dfs(d.children) } }
  dfs(deptTree.value); deptMap.value=m
}
async function loadTypeOptions(){
  try{
    const res:any=await request.post('/role/queryByPage', {pageNo:1,pageSize:50,data:{}})
    const lst=res?.data?.list ?? []
    if(lst.length){
      // 角色联动：用角色表驱动类型下拉，新增角色自动出现
      typeOptions.value=lst.map((r:any)=> ({label:r.role_name, value:String(r.role_id)}))
      // 同时建立映射用于表格显示
      const m:Record<string,string>={}
      for(const r of lst) m[String(r.role_id)]=r.role_name
      // 保留 0/1/2 兼容旧数据
      m['0']=m['1']? '管理员' : '管理员'
      if(!m['1']) m['1']='教师'
      if(!m['2']) m['2']='学生'
      // 合并旧映射
      typeMap.value={...{'0':'管理员','1':'教师','2':'学生'}, ...m}
    }
  }catch{}
}
onMounted(()=>{ loadDepts(); loadTypeOptions() })
const dialog=ref(false)
const form=reactive<any>({userId:'', workNo:'', userName:'', phone:'', password:'', deptId:'', userType:'0', status:'0'})
const isSuperAdmin=computed(()=> String(form.userType)==='1')
const workNoRuleTip=computed(()=>{
  if(isSuperAdmin.value) return '超级管理员 0'
  if(String(form.userType)==='6') return '教务处 0001、0002…'
  const cid=form.deptId? String(form.deptId).padStart(4,'0') : '学院0001'
  return `${cid}+00001 如 000100001`
})
watch(()=> form.userType, (v)=>{ if(String(v)==='1'){ form.workNo='0'; form.deptId='' } })
function openEdit(row?:any){
  if(row){
    form.userId=row.user_id; form.workNo=row.work_no||''; form.userName=row.user_name; form.phone=row.phone; form.password=''; form.deptId=row.dept_id; form.userType=row.user_type; form.status=row.status
    if(isSuperAdmin.value) form.workNo='0'
  } else { form.userId=''; form.workNo=''; form.userName=''; form.phone=''; form.password=''; form.deptId=''; form.userType='0'; form.status='0' } dialog.value=true
}
async function submit(){ await request.post('/user/insertOrUpdate', {userId:form.userId||undefined, workNo:form.workNo||undefined, userName:form.userName, phone:form.phone, password:form.password||undefined, deptId:form.deptId?Number(form.deptId):null, userType:form.userType, status:form.status}); ElMessage.success('保存成功'); dialog.value=false; fetch() }
async function del(row:any){ await request.post(`/user/delete/${row.user_id}`); ElMessage.success('已停用'); fetch() }
const roleDialog=ref(false); const roles=ref<any[]>([]); const roleIds=ref<number[]>([]); let curUserId:any=null
async function openRole(row:any){ curUserId=row.user_id; const res:any = await request.post('/role/queryByPage', {pageNo:1,pageSize:20,data:{}}); roles.value=res.data.list||[]; roleIds.value=[]; roleDialog.value=true }
async function saveRole(){ await request.post('/user/save', {userId:curUserId, roleIds:roleIds.value}); ElMessage.success('已分配角色'); roleDialog.value=false }
</script>
