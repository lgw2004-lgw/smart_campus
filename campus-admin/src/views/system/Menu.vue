<template>
  <div>
    <el-card shadow="never" style="border-radius:14px;border:1px solid #e6ebf5">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="width:40px;height:40px;background:linear-gradient(135deg,#1e5eff,#5b8cff);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff"><el-icon><Menu /></el-icon></div>
          <div>
            <div style="font-size:16px;font-weight:800">菜单管理</div>
            <div style="font-size:12px;color:#8a94a6">GET /menu/queryTreeDataByUserId · 按角色过滤 · 树形展示</div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <el-input v-model="userId" placeholder="按用户ID过滤(留空全部)" clearable style="width:200px" prefix-icon="User" />
          <el-button type="primary" @click="load" :icon="Search">加载</el-button>
        </div>
      </div>
    </el-card>

    <el-row>
      <el-col :span="24">
        <el-card shadow="never" style="border-radius:14px;border:1px solid #e6ebf5;min-height:520px">
          <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:700">菜单树</span><div><el-tag type="info" size="small">{{ flatCount }} 个菜单</el-tag><el-button size="small" type="success" style="margin-left:8px" @click="openEdit()">新增菜单</el-button></div></div></template>
          <el-tree
            :data="tree"
            :props="{label:'menu_name', children:'children'}"
            default-expand-all
            :expand-on-click-node="false"
            class="menu-tree"
          >
            <template #default="{ data }">
              <div class="tree-node">
                <div class="node-left">
                  <div class="icon-box" :style="{background: data.parent_id===0?'#eef3ff':'#f6f8ff', color: data.parent_id===0?'#1e5eff':'#5b8cff'}">
                    <el-icon><component :is="iconMap[data.icon] || 'Menu'" /></el-icon>
                  </div>
                  <div>
                    <div class="node-title">{{ data.menu_name }}</div>
                    <div class="node-path">{{ data.path || '—' }}</div>
                  </div>
                </div>
                <div class="node-right">
                  <el-tag size="small" effect="plain" type="info">ID {{ data.menu_id }}</el-tag>
                  <el-tag size="small" effect="plain">排序 {{ data.sort ?? 0 }}</el-tag>
                  <el-button size="small" @click.stop="openEdit(data)">编辑</el-button>
                  <el-button size="small" type="danger" @click.stop="removeRow(data)">删除</el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="dialog" :title="form.menuId?'编辑菜单':'新增菜单'" width="520">
      <el-form :model="form" label-width="90px">
        <el-form-item label="菜单名"><el-input v-model="form.menuName"/></el-form-item>
        <el-form-item label="上级">
          <el-tree-select v-model="form.parentId" :data="tree" :props="{label:'menu_name', value:'menu_id', children:'children'}" check-strictly placeholder="选择上级，顶级为空" clearable style="width:100%" />
        </el-form-item>
        <el-form-item label="路径"><el-input v-model="form.path" placeholder="/academic/course"/></el-form-item>
        <el-form-item label="图标"><el-input v-model="form.icon" placeholder="House/Reading/... 对应 @element-plus/icons-vue"/></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Menu, House, Reading, User, Box, Wallet, Document, Setting } from '@element-plus/icons-vue'
const userId=ref('')
const tree=ref<any[]>([])
const iconMap:any = { House, Reading, User, Box, Wallet, Document, Setting, Menu }
async function load(){
  const res:any = await request.get('/menu/queryTreeDataByUserId', {params: userId.value?{userId:userId.value}:{}})
  tree.value=res.data||[]
}
const dialog=ref(false)
const form=reactive<any>({menuId:'', menuName:'', parentId:null, path:'', icon:'', sort:0})
function openEdit(data?:any){
  if(data){ form.menuId=data.menu_id; form.menuName=data.menu_name; form.parentId=data.parent_id||null; form.path=data.path||''; form.icon=data.icon||''; form.sort=data.sort||0 }
  else{ form.menuId=''; form.menuName=''; form.parentId=null; form.path=''; form.icon=''; form.sort=0 }
  dialog.value=true
}
async function submit(){
  if(!form.menuName) return ElMessage.warning('菜单名必填')
  await request.post('/menu/save', {menuId:form.menuId||undefined, menuName:form.menuName, parentId:form.parentId||0, path:form.path, icon:form.icon, sort:form.sort})
  ElMessage.success('保存成功'); dialog.value=false; load()
}
async function removeRow(data:any){
  try{ await ElMessageBox.confirm(`确认删除菜单「${data.menu_name}」？`, '删除', {type:'warning'}) } catch{ return }
  try{ await request.post(`/menu/delete/${data.menu_id}`); ElMessage.success('已删除'); load() } catch(e:any){ ElMessage.error(e.message||'删除失败，存在下级') }
}
const flatCount=computed(()=>{
  let n=0; const dfs=(arr:any[])=>{ for(const x of arr){ n++; if(x.children) dfs(x.children) } }; dfs(tree.value); return n
})
onMounted(load)
</script>
<style scoped>
.menu-tree :deep(.el-tree-node__content){height:auto;padding:6px 8px;border-radius:8px;margin:2px 0}
.menu-tree :deep(.el-tree-node__content:hover){background:#f6f8ff}
.tree-node{display:flex;align-items:center;justify-content:space-between;flex:1;gap:12px}
.node-left{display:flex;align-items:center;gap:10px}
.icon-box{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center}
.node-title{font-weight:600;font-size:13px;color:#1f2a3a}
.node-path{font-size:12px;color:#8a94a6}
.node-right{display:flex;align-items:center;gap:6px}
</style>
