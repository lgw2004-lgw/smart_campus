<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>宿舍管理 · 楼栋/房间/分配/调宿/退宿</h3>
      <div style="display:flex;gap:6px;flex-wrap:wrap">
        <el-select v-model="query.buildingId" placeholder="按楼栋筛选" clearable style="width:160px" @clear="search" @change="search">
          <el-option v-for="b in buildingOptions" :key="b.building_id" :label="b.building_name" :value="b.building_id"/>
        </el-select>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button type="success" @click="openRoom()">新增房间</el-button>
        <el-button @click="openBuilding()">新增楼栋</el-button>
        <el-button type="success" plain @click="dialogAssign=true">分配宿舍</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="room_no" label="房号" width="100"/>
      <el-table-column label="楼栋" width="140"><template #default="{row}">{{ buildingMap[row.building_id] || row.building_id }}</template></el-table-column>
      <el-table-column prop="capacity" label="容量" width="80"/>
      <el-table-column prop="occupied" label="已住" width="80"><template #default="{row}"><el-tag :type="row.occupied>=row.capacity?'danger':'success'">{{ row.occupied }}/{{ row.capacity }}</el-tag></template></el-table-column>
      <el-table-column prop="status" label="状态" width="80"/>
      <el-table-column label="操作" width="300"><template #default="{row}">
        <el-button size="small" @click="openRoom(row)">编辑</el-button>
        <el-button size="small" type="danger" @click="doDeleteRoom(row)">删除</el-button>
        <el-button size="small" @click="openExchange(row)">调宿</el-button>
      </template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />

    <el-card shadow="never" style="margin-top:14px">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:600">楼栋列表</span><span style="font-size:12px;color:#999">{{ buildingOptions.length }}栋</span></div></template>
      <el-table :data="buildingOptions" border size="small">
        <el-table-column prop="building_id" label="楼栋ID" width="90"/>
        <el-table-column prop="building_name" label="楼栋名"/>
        <el-table-column prop="floors" label="层数" width="80"/>
        <el-table-column prop="status" label="状态" width="80"/>
        <el-table-column label="操作" width="140"><template #default="{row}"><el-button size="small" type="danger" @click="doDeleteBuilding(row)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogRoom" :title="roomForm.roomId?'编辑房间':'新增房间'" width="480">
      <el-form :model="roomForm" label-width="80px">
        <el-form-item label="楼栋"><el-select v-model="roomForm.buildingId" placeholder="选择楼栋" style="width:100%"><el-option v-for="b in buildingOptions" :key="b.building_id" :label="b.building_name" :value="b.building_id"/></el-select></el-form-item>
        <el-form-item label="房号"><el-input v-model="roomForm.roomNo" placeholder="如 101"/></el-form-item>
        <el-form-item label="容量"><el-input-number v-model="roomForm.capacity" :min="1" :max="8"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogRoom=false">取消</el-button><el-button type="primary" @click="submitRoom">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="dialogBuilding" title="新增楼栋" width="420">
      <el-form :model="buildingForm" label-width="80px">
        <el-form-item label="楼栋名"><el-input v-model="buildingForm.buildingName" placeholder="如 学1栋"/></el-form-item>
        <el-form-item label="层数"><el-input-number v-model="buildingForm.floors" :min="1" :max="20"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogBuilding=false">取消</el-button><el-button type="primary" @click="submitBuilding">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="dialogAssign" title="分配宿舍" width="500">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="学号"><el-input v-model="assignForm.studentId" placeholder="20240101"/></el-form-item>
        <el-form-item label="楼栋"><el-select v-model="assignForm.buildingId" placeholder="选择楼栋" style="width:100%"><el-option v-for="b in buildingOptions" :key="b.building_id" :label="b.building_name" :value="b.building_id"/></el-select></el-form-item>
        <el-form-item label="房间"><el-select v-model="assignForm.roomId" placeholder="选择房间" style="width:100%"><el-option v-for="r in list" :key="r.room_id" :label="`${buildingMap[r.building_id]||r.building_id} - ${r.room_no} (${r.occupied}/${r.capacity})`" :value="r.room_id"/></el-select></el-form-item>
        <el-form-item label="床位"><el-input-number v-model="assignForm.bedNo" :min="1" :max="6"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogAssign=false">取消</el-button><el-button type="primary" @click="doAssign">分配</el-button></template>
    </el-dialog>

    <el-dialog v-model="dialogExchange" title="调宿" width="500">
      <el-form :model="exchangeForm" label-width="80px">
        <el-form-item label="学号"><el-input v-model="exchangeForm.studentId"/></el-form-item>
        <el-form-item label="新房间"><el-select v-model="exchangeForm.roomId" placeholder="选择房间" style="width:100%"><el-option v-for="r in list" :key="r.room_id" :label="`${buildingMap[r.building_id]||r.building_id} - ${r.room_no}`" :value="r.room_id"/></el-select></el-form-item>
        <el-form-item label="床位"><el-input-number v-model="exchangeForm.bedNo" :min="1" :max="6"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogExchange=false">取消</el-button><el-button type="primary" @click="doExchange">确认调宿</el-button></template>
    </el-dialog>

    <el-dialog v-model="dialogCheckout" title="退宿" width="400">
      <el-form :model="checkoutForm" label-width="80px">
        <el-form-item label="学号"><el-input v-model="checkoutForm.studentId"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogCheckout=false">取消</el-button><el-button type="danger" @click="doCheckout">退宿</el-button></template>
    </el-dialog>
    <div style="margin-top:12px"><el-button size="small" type="info" @click="dialogCheckout=true">按学号退宿</el-button></div>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/dorm/queryByPage', {buildingId:''} as any)
fetch()

const buildingOptions=ref<any[]>([])
const buildingMap=ref<Record<string,string>>({})
async function loadBuildings(){
  const res:any=await request.post('/building/queryByPage', {pageNo:1,pageSize:50,data:{}})
  buildingOptions.value=res.data.list||[]
  const m:Record<string,string>={}; for(const b of buildingOptions.value) m[b.building_id]=b.building_name; buildingMap.value=m
}
onMounted(loadBuildings)

// 房间增改删
const dialogRoom=ref(false)
const roomForm=reactive<any>({roomId:'', buildingId:'', roomNo:'', capacity:4})
function openRoom(row?:any){
  if(row){ roomForm.roomId=row.room_id; roomForm.buildingId=row.building_id; roomForm.roomNo=row.room_no; roomForm.capacity=row.capacity }
  else{ roomForm.roomId=''; roomForm.buildingId=''; roomForm.roomNo=''; roomForm.capacity=4 }
  dialogRoom.value=true
}
async function submitRoom(){
  if(!roomForm.buildingId||!roomForm.roomNo) return ElMessage.warning('楼栋和房号必填')
  await request.post('/room/save', {roomId:roomForm.roomId||undefined, buildingId:Number(roomForm.buildingId), roomNo:roomForm.roomNo, capacity:roomForm.capacity})
  ElMessage.success('保存成功'); dialogRoom.value=false; fetch()
}
async function doDeleteRoom(row:any){
  try{ await ElMessageBox.confirm(`确认删除房间 ${buildingMap.value[row.building_id]||row.building_id} - ${row.room_no}？`, '删除', {type:'warning'}) } catch{ return }
  try{ await request.post(`/room/delete/${row.room_id}`); ElMessage.success('已删除'); fetch() } catch(e:any){ ElMessage.error(e.message||'删除失败，房间已分配') }
}

// 楼栋
const dialogBuilding=ref(false)
const buildingForm=reactive<any>({buildingName:'', floors:6})
function openBuilding(){ buildingForm.buildingName=''; buildingForm.floors=6; dialogBuilding.value=true }
async function submitBuilding(){
  if(!buildingForm.buildingName) return ElMessage.warning('楼栋名必填')
  await request.post('/building/save', {buildingName:buildingForm.buildingName, floors:buildingForm.floors})
  ElMessage.success('保存成功'); dialogBuilding.value=false; loadBuildings()
}
async function doDeleteBuilding(row:any){
  try{ await ElMessageBox.confirm(`确认删除楼栋 ${row.building_name}？需先清空房间`, '删除', {type:'warning'}) } catch{ return }
  try{ await request.post(`/building/delete/${row.building_id}`); ElMessage.success('已删除'); loadBuildings(); fetch() } catch(e:any){ ElMessage.error(e.message||'删除失败，存在房间') }
}

const dialogAssign=ref(false); const assignForm=reactive<any>({studentId:'', buildingId:'', roomId:'', bedNo:1})
async function doAssign(){ if(!assignForm.studentId) return ElMessage.warning('学号必填'); await request.post('/dorm/assign', {studentId:assignForm.studentId, buildingId:Number(assignForm.buildingId), roomId:Number(assignForm.roomId), bedNo:assignForm.bedNo}); ElMessage.success('分配成功'); dialogAssign.value=false; fetch() }
const dialogExchange=ref(false); const exchangeForm=reactive<any>({studentId:'', roomId:'', bedNo:1})
function openExchange(row:any){ exchangeForm.roomId=''; exchangeForm.bedNo=1; dialogExchange.value=true }
async function doExchange(){ await request.post('/dorm/exchange', {studentId:exchangeForm.studentId, roomId:Number(exchangeForm.roomId), bedNo:exchangeForm.bedNo}); ElMessage.success('调宿成功'); dialogExchange.value=false; fetch() }
const dialogCheckout=ref(false); const checkoutForm=reactive<any>({studentId:''})
async function doCheckout(){ await request.post('/dorm/checkout', {studentId:checkoutForm.studentId}); ElMessage.success('已退宿'); dialogCheckout.value=false; fetch() }
</script>
