<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>角色管理</h3>
      <div>
        <el-input v-model="query.roleName" placeholder="角色名" clearable style="width:160px;margin-right:8px" @clear="search" @keyup.enter="search"/>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openEdit()">新增角色</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="role_id" label="ID" width="90"/>
      <el-table-column prop="role_name" label="角色名"/>
      <el-table-column prop="role_code" label="编码" width="180"/>
      <el-table-column prop="status" label="状态" width="90"><template #default="{row}"><el-tag :type="row.status==='0'?'success':'info'">{{ row.status==='0'?'正常':'停用' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="320"><template #default="{row}">
        <el-button size="small" @click="openEdit(row)">编辑</el-button>
        <el-button size="small" type="warning" @click="openMenu(row)">分配菜单</el-button>
        <el-button size="small" type="danger" @click="removeRow(row)">删除</el-button>
      </template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="formDialog" :title="form.roleId?'编辑角色':'新增角色'" width="500">
      <el-form :model="form" label-width="80px">
        <el-form-item label="角色名"><el-input v-model="form.roleName" placeholder="如 辅导员" @input="onNameInput" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="form.roleCode" placeholder="role:cs_jwc 唯一 · 自动为拼音首字母" @input="onCodeManual" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="正常" value="0"/><el-option label="停用" value="1"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="formDialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="dialog" title="分配菜单 → /role/roleMenu/add" width="600">
      <el-tree :data="menus" :props="{label:'menu_name', children:'children'}" show-checkbox node-key="menu_id" ref="treeRef" check-strictly/>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pinyin } from 'pinyin-pro'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/role/queryByPage', {roleName:''})
fetch()

const formDialog=ref(false)
const form=reactive<any>({roleId:'', roleName:'', roleCode:'', status:'0'})
let isCodeManuallyEdited=false
let lastAutoCode=''
function openEdit(row?:any){
  if(row){ form.roleId=row.role_id; form.roleName=row.role_name; form.roleCode=row.role_code; form.status=row.status; isCodeManuallyEdited=true; lastAutoCode=form.roleCode }
  else{ form.roleId=''; form.roleName=''; form.roleCode=''; form.status='0'; isCodeManuallyEdited=false; lastAutoCode='' }
  formDialog.value=true
}
function toCode(name:string){
  const s=name.trim()
  if(!s) return ''
  // 含中文则用拼音首字母，否则用英文小写下划线
  const hasZh=/[\u4e00-\u9fa5]/.test(s)
  let base=''
  if(hasZh){
    try{
      const arr=pinyin(s, { pattern:'initial', toneType:'none', type:'array' }) as string[]
      base=arr.join('').replace(/[^a-z0-9]/g,'')
    } catch{ base=s.replace(/\s+/g,'_') }
  } else {
    base=s.toLowerCase().replace(/\s+/g,'_').replace(/[^a-z0-9_]/g,'')
  }
  base=base.slice(0,24) // 留出 role: 前缀后不超过30
  return 'role:'+base
}
function onNameInput(val:string){
  if(form.roleId) return // 编辑时不联动
  if(isCodeManuallyEdited) return
  const auto=toCode(val)
  if(!form.roleCode || form.roleCode===lastAutoCode){
    form.roleCode=val?auto:''
    lastAutoCode=auto
  }
}
function onCodeManual(){ isCodeManuallyEdited=true }
async function submit(){
  if(!form.roleName) return ElMessage.warning('角色名必填')
  await request.post('/role/save', {roleId:form.roleId||undefined, roleName:form.roleName, roleCode:form.roleCode||undefined, status:form.status})
  ElMessage.success('保存成功'); formDialog.value=false; fetch()
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除角色「${row.role_name}」？`, '删除', {type:'warning'}) } catch{ return }
  try{
    await request.post(`/role/delete/${row.role_id}`)
    ElMessage.success('已删除'); fetch()
  } catch(e:any){ ElMessage.error(e.message||'删除失败，可能已分配用户') }
}

const dialog=ref(false); const menus=ref<any[]>([]); const treeRef=ref<any>(); let curRoleId:any=null
async function openMenu(row:any){
  curRoleId=row.role_id
  const res:any = await request.get('/menu/queryTreeDataByUserId')
  menus.value=res.data||[]
  dialog.value=true
}
async function save(){
  const ids = treeRef.value.getCheckedKeys().concat(treeRef.value.getHalfCheckedKeys())
  await request.post('/role/roleMenu/add', {roleId:curRoleId, menuIds:ids})
  ElMessage.success('已分配菜单'); dialog.value=false
}
</script>
