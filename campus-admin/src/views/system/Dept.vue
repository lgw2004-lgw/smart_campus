<template>
  <div>
    <el-card shadow="never" style="border-radius:14px;border:1px solid #e6ebf5">
      <div style="display:flex;align-items:center;gap:12px">
        <div style="width:40px;height:40px;background:linear-gradient(135deg,#1e5eff,#5b8cff);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff"><el-icon><OfficeBuilding /></el-icon></div>
        <div>
          <div style="font-size:16px;font-weight:800">院系管理 · 学院-专业-班级</div>
          <div style="font-size:12px;color:#8a94a6">示例：计算机与软件工程学院 → 软件工程 → 2022软件工程1班（班级在“班级管理”）</div>
        </div>
        <el-tag type="info" effect="plain" style="margin-left:auto">学院-专业 + 班级表</el-tag>
      </div>
    </el-card>

    <el-row :gutter="16" style="margin-top:14px">
      <el-col :span="9">
        <el-card shadow="never" style="border-radius:14px;border:1px solid #e6ebf5;min-height:520px">
          <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:700">组织树</span><div style="display:flex;gap:6px"><el-button size="small" @click="expandAll">展开全部</el-button><el-button size="small" @click="collapseAll">收起全部</el-button><el-button size="small" @click="loadTree">刷新</el-button></div></div></template>
          <el-tree ref="treeRef" :data="tree" :props="{label:'dept_name', children:'children'}" default-expand-all @node-click="onNodeClick" class="dept-tree">
            <template #default="{ data }">
              <div style="display:flex;align-items:center;gap:6px">
                <el-tag size="small" :type="data.level===0?'warning':'success'" effect="plain">{{ data.levelLabel }}</el-tag>
                <span style="font-weight:600;font-size:13px">{{ data.dept_name }}</span>
                <span style="font-size:12px;color:#999">ID{{ data.dept_id }}</span>
              </div>
            </template>
          </el-tree>
        </el-card>
      </el-col>
      <el-col :span="15">
        <el-card shadow="never" style="border-radius:14px;border:1px solid #e6ebf5">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div style="font-weight:700">院系列表 <span v-if="selectedDept" style="font-weight:400;color:#8a94a6">（当前：{{ selectedDept.dept_name }}）</span></div>
            <div style="display:flex;gap:8px;align-items:center">
              <el-button v-if="selectedDept" size="small" @click="showChildren">查看下级</el-button>
              <el-button v-if="selectedDept" size="small" @click="clearTreeFilter">显示全部</el-button>
              <el-input v-model="query.deptName" placeholder="院系/专业名" clearable style="width:140px" @clear="clearTreeFilter" @keyup.enter="handleSearch"/>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button type="success" @click="openEdit()">新增</el-button>
            </div>
          </div>
          <el-table :data="list" v-loading="loading" border size="small">
            <el-table-column prop="dept_id" label="ID" width="70"/>
            <el-table-column prop="dept_name" label="名称"/>
            <el-table-column label="层级" width="90"><template #default="{row}"><el-tag size="small" :type="levelOf(row)==='学院'?'warning':'success'">{{ levelOf(row) }}</el-tag></template></el-table-column>
            <el-table-column prop="parent_id" label="父ID" width="80"/>
            <el-table-column prop="order_num" label="排序" width="70"/>
            <el-table-column label="操作" width="170"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
          </el-table>
          <el-pagination style="margin-top:10px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialog" :title="form.deptId?'编辑':'新增院系/专业'" width="520">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.deptName" placeholder="如 软件工程" /></el-form-item>
        <el-form-item label="上级">
          <el-tree-select v-model="form.parentId" :data="tree" :props="{label:'dept_name', value:'dept_id', children:'children'}" check-strictly placeholder="选择所属学院，顶级为空即学院" clearable style="width:100%" />
          <div style="font-size:12px;color:#8a94a6;margin-top:4px">顶级 parent=0 为学院，专业 parent=所属学院</div>
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.orderNum" :min="0"/></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="正常" value="0"/><el-option label="停用" value="1"/></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/dept/queryByPage', {deptName:'', deptId:'', parentId:''})
fetch()
const tree=ref<any[]>([])
const treeRef=ref<any>(null)
const selectedDept=ref<any>(null)
async function loadTree(){ const res:any=await request.get('/dept/tree'); tree.value=res.data||[] }
function expandAll(){ const m=(treeRef.value as any)?.store?.nodesMap; if(m){ Object.values(m).forEach((n:any)=> n.expanded=true) } }
function collapseAll(){ const m=(treeRef.value as any)?.store?.nodesMap; if(m){ Object.values(m).forEach((n:any)=> n.expanded=false) } }
function onNodeClick(data:any){
  selectedDept.value=data
  // 点击树节点仅显示该节点自身信息，不含下级专业
  query.deptId=data.dept_id
  query.deptName=''
  ;(query as any).parentId=''
  search()
}
function clearTreeFilter(){
  selectedDept.value=null
  query.deptId=''
  query.deptName=''
  ;(query as any).parentId=''
  search()
}
function showChildren(){
  if(!selectedDept.value) return
  query.deptId=''
  query.deptName=''
  ;(query as any).parentId=selectedDept.value.dept_id
  search()
}
function levelOf(row:any){
  const find=(arr:any[], id:number):any=>{ for(const a of arr){ if(a.dept_id===id) return a; const c=find(a.children||[], id); if(c) return c } return null }
  const node=find(tree.value, row.dept_id)
  return node?.levelLabel || '-'
}
function handleSearch(){
  // 按名称搜索时清除树节点筛选，避免 deptId 与 deptName 叠加导致无结果
  if(query.deptName){
    selectedDept.value=null
    query.deptId=''
    ;(query as any).parentId=''
  }
  search()
}
const dialog=ref(false)
const form=reactive<any>({deptId:'', deptName:'', parentId:null, orderNum:0, status:'0'})
function openEdit(row?:any){
  if(row){ form.deptId=row.dept_id; form.deptName=row.dept_name; form.parentId=row.parent_id||null; form.orderNum=row.order_num; form.status=row.status }
  else{ form.deptId=''; form.deptName=''; form.parentId=selectedDept.value?selectedDept.value.dept_id:null; form.orderNum=0; form.status='0' }
  dialog.value=true
}
async function submit(){
  if(!form.deptName) return ElMessage.warning('名称必填')
  await request.post('/dept/save', {deptId:form.deptId||undefined, deptName:form.deptName, parentId:form.parentId||0, orderNum:form.orderNum, status:form.status})
  ElMessage.success('保存成功'); dialog.value=false; fetch(); loadTree()
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除「${row.dept_name}」？存在下级或用户将失败`, '删除', {type:'warning'}) } catch{ return }
  try{ await request.post(`/dept/delete/${row.dept_id}`); ElMessage.success('已删除'); fetch(); loadTree() } catch(e:any){ ElMessage.error(e.message||'删除失败') }
}
onMounted(loadTree)
</script>
<style scoped>
.dept-tree :deep(.el-tree-node__content){height:auto;padding:4px 6px}
</style>
