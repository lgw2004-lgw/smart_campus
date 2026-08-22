<template>
  <el-card>
    <h3>字典管理 · dictType/dictData + 公共 /dictData/type/{type}</h3>
    <el-tabs>
      <el-tab-pane label="字典类型">
        <el-table :data="typeList" v-loading="typeLoading" border>
          <el-table-column prop="dict_id" label="ID" width="90"/>
          <el-table-column prop="dict_name" label="名称"/>
          <el-table-column prop="dict_type" label="类型" width="200"/>
          <el-table-column label="操作" width="120"><template #default="{row}"><el-button size="small" @click="loadData(row.dict_type)">查看数据</el-button></template></el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="字典数据">
        <div style="margin-bottom:8px"><el-input v-model="dataQuery.dictType" placeholder="dictType 如 sys_user_sex" clearable style="width:200px;margin-right:8px"/><el-button @click="loadData(dataQuery.dictType)">查询</el-button><el-button @click="testPublic">测试公共接口</el-button></div>
        <el-table :data="dataList" v-loading="dataLoading" border>
          <el-table-column prop="dict_code" label="编码" width="90"/>
          <el-table-column prop="dict_type" label="类型" width="160"/>
          <el-table-column prop="dict_label" label="标签" width="120"/>
          <el-table-column prop="dict_value" label="键值" width="100"/>
          <el-table-column prop="dict_sort" label="排序" width="80"/>
        </el-table>
        <div v-if="publicData.length" style="margin-top:8px"><el-tag v-for="d in publicData" :key="d.dict_code" style="margin-right:6px">{{ d.dict_label }}={{ d.dict_value }}</el-tag></div>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const typeList=ref<any[]>([]); const typeLoading=ref(false)
async function loadType(){ typeLoading.value=true; const res:any = await request.post('/dictType/queryByPage', {pageNo:1,pageSize:20,data:{}}); typeList.value=res.data.list||[]; typeLoading.value=false }
const dataList=ref<any[]>([]); const dataLoading=ref(false); const dataQuery=reactive<any>({dictType:'sys_user_sex'})
async function loadData(type?:string){ const t=type||dataQuery.dictType; if(!t) return; dataLoading.value=true; const res:any = await request.post('/dictData/queryByPage', {pageNo:1,pageSize:20,data:{dictType:t}}); dataList.value=res.data.list||[]; dataLoading.value=false }
const publicData=ref<any[]>([])
async function testPublic(){ if(!dataQuery.dictType) return; const res:any = await request.get(`/dictData/type/${dataQuery.dictType}`); publicData.value=res.data||[]; ElMessage.success('公共接口已返回') }
onMounted(()=>{ loadType(); loadData() })
</script>
