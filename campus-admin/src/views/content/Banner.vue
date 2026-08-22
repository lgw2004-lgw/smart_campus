<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>轮播管理 · C端看板消费 /banner/loadBanner(enabled=1)</h3>
      <div>
        <el-button type="primary" @click="search">刷新</el-button>
        <el-button type="success" @click="openEdit()">新增轮播</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="id" label="ID" width="70"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column label="图片" width="200"><template #default="{row}"><el-image :src="row.url" style="width:160px;height:50px" fit="cover"/></template></el-table-column>
      <el-table-column prop="position" label="排序" width="70"/>
      <el-table-column prop="enabled" label="启用" width="80"><template #default="{row}"><el-tag :type="row.enabled?'success':'info'">{{ row.enabled?'启用':'禁用' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="180"><template #default="{row}"><el-button size="small" @click="openEdit(row)">编辑</el-button><el-button size="small" type="danger" @click="removeRow(row)">删除</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-dialog v-model="dialog" :title="form.id?'编辑轮播':'新增轮播'" width="520">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="图片">
          <div style="width:100%">
            <div style="display:flex;align-items:center;gap:10px">
              <el-upload :action="uploadUrl" :headers="uploadHeaders" :show-file-list="false" :on-success="onUploadSuccess" :on-error="onUploadError" accept="image/*">
                <el-button type="primary" size="small">本地上传</el-button>
              </el-upload>
              <span style="font-size:12px;color:#8a94a6">或填写线上地址</span>
            </div>
            <el-input v-model="form.url" placeholder="https://... 或 /media/banner/xxx.png" style="margin-top:6px"/>
            <el-image v-if="form.url" :src="form.url" style="width:180px;height:60px;margin-top:6px;border-radius:6px" fit="cover"/>
          </div>
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.position" :min="0"/></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
    </el-dialog>

    <el-divider/>
    <h4>前台预览（/banner/loadBanner）</h4>
    <el-carousel height="160px" v-if="banners.length"><el-carousel-item v-for="b in banners" :key="b.id"><img :src="b.url" style="width:100%;height:160px;object-fit:cover"/><div style="position:absolute;bottom:10px;left:10px;color:#fff;background:rgba(0,0,0,.5);padding:2px 8px">{{ b.name }}</div></el-carousel-item></el-carousel>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/banner/queryByPage', {})
fetch()
const banners=ref<any[]>([])
async function loadPreview(){ const res:any = await request.get('/banner/loadBanner'); banners.value=res.data||[] }
onMounted(loadPreview)

const dialog=ref(false)
const form=reactive<any>({id:'', name:'', url:'', position:0, enabled:true})
const uploadUrl='/banner/upload'
const uploadHeaders=()=>({token:localStorage.getItem('token')||''})
function onUploadSuccess(res:any){
  if(res.code===200){ form.url=res.data.url; ElMessage.success('上传成功') }
  else ElMessage.error(res.message||'上传失败')
}
function onUploadError(){ ElMessage.error('上传失败') }
function openEdit(row?:any){
  if(row){ form.id=row.id; form.name=row.name; form.url=row.url; form.position=row.position; form.enabled=!!row.enabled }
  else{ form.id=''; form.name=''; form.url=''; form.position=0; form.enabled=true }
  dialog.value=true
}
async function submit(){
  if(!form.name||!form.url) return ElMessage.warning('名称与图片URL必填')
  await request.post('/banner/save', {id:form.id||undefined, name:form.name, url:form.url, position:form.position, enabled:form.enabled?1:0})
  ElMessage.success('保存成功'); dialog.value=false; fetch(); loadPreview()
}
async function removeRow(row:any){
  try{ await ElMessageBox.confirm(`确认删除轮播「${row.name}」？`, '删除', {type:'warning'}) } catch{ return }
  await request.post(`/banner/delete/${row.id}`)
  ElMessage.success('已删除'); fetch(); loadPreview()
}
</script>
