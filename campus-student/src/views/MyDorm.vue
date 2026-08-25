<template>
  <div>
    <el-card shadow="never" style="border-radius:14px;background:linear-gradient(135deg,#1e5eff,#5b8cff);color:#fff">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div><div style="font-size:13px;opacity:.9">我的宿舍</div><div style="font-size:20px;font-weight:800;margin-top:4px">{{ assign ? `${assign.building_id}栋 · ${assign.room_id}房 · ${assign.bed_no}号床` : '尚未分配宿舍' }}</div><div style="font-size:12px;opacity:.85;margin-top:4px">与管理端宿舍管理实时联动 · 已住/容量实时更新</div></div>
        <el-icon :size="48" style="opacity:.2"><OfficeBuilding /></el-icon>
      </div>
      <div style="margin-top:12px;display:flex;gap:8px" v-if="assign">
        <el-button size="small" color="#fff" style="color:#1e5eff" @click="doCheckout">申请退宿</el-button>
        <el-button size="small" plain style="background:rgba(255,255,255,.15);color:#fff;border-color:rgba(255,255,255,.3)" @click="selected && doExchange()">调宿到已选</el-button>
      </div>
    </el-card>

    <div style="margin-top:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
      <h3 style="margin:0">可选房源</h3>
      <div style="display:flex;gap:8px;align-items:center">
        <el-select v-model="selectedCollege" placeholder="选择书院" clearable style="width:180px" @change="loadRooms">
          <el-option v-for="c in colleges" :key="c.dept_id" :label="c.dept_name" :value="c.dept_id" />
        </el-select>
        <el-tag type="info">点击卡片选择</el-tag>
      </div>
    </div>
    <el-alert v-if="!isPublishOpen" title="宿舍选房未发布或已截止，暂不可选" type="warning" show-icon :closable="false" style="margin-top:8px" />
    <div class="dorm-grid">
      <div class="dorm-card" v-for="r in rooms" :key="r.room_id" :class="{selected: selected?.room_id===r.room_id, full: r.occupied>=r.capacity || !isPublishOpen}" @click="isPublishOpen && (selected=r)">
        <div class="dorm-head"><span class="room-no">{{ buildingMap[r.building_id]?.building_name || r.building_id }}栋 {{ r.room_no }}</span><span class="occupy" :class="{danger: r.occupied>=r.capacity}">{{ r.occupied }}/{{ r.capacity }}</span></div>
        <div style="font-size:12px;color:#5a6b8a;margin-top:4px">书院：{{ collegeMap[buildingMap[r.building_id]?.dept_id] || '-' }}</div>
        <el-progress :percentage="(r.occupied/r.capacity)*100" :show-text="false" :stroke-width="6" :color="r.occupied>=r.capacity?'#ff4d4f':'#1e5eff'" style="margin:8px 0"/>
        <div style="font-size:12px;color:#8a94a6">房间ID {{ r.room_id }} · {{ !isPublishOpen?'未发布': r.occupied>=r.capacity?'已满':'可选' }}</div>
        <el-button v-if="selected?.room_id===r.room_id" size="small" type="primary" round style="margin-top:8px;width:100%" :disabled="!isPublishOpen || r.occupied>=r.capacity" @click.stop="doAssign()">{{ assign?'调宿':'选此宿舍' }}</el-button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const rooms=ref<any[]>([]); const selected=ref<any>(null); const assign=ref<any>(null)
const selectedCollege=ref<number|null>(null)
const colleges=ref<any[]>([])
const collegeMap=ref<Record<string,string>>({})
const buildingMap=ref<Record<string,any>>({})
const publishList=ref<any[]>([])
const isPublishOpen=computed(()=>{
  if(!publishList.value.length) return false
  const now=new Date()
  for(const p of publishList.value){
    if(p.is_published!=='1') continue
    if(p.end_time && new Date(p.end_time) < now) continue
    if(p.start_time && new Date(p.start_time) > now) continue
    if(!p.college_id) return true
    if(selectedCollege.value && p.college_id==selectedCollege.value) return true
    if(!selectedCollege.value) return true
  }
  return false
})

async function loadMeta(){
  try{
    const d:any=await request.get('/dept/tree')
    const map:Record<string,string>={}
    const cols:any[]=[]
    const walk=(arr:any[])=>{ for(const n of arr){ map[n.dept_id]=n.dept_name; if(n.parent_id===0) cols.push(n); if(n.children) walk(n.children)} }
    walk(d.data||[])
    collegeMap.value=map
    colleges.value=cols
  }catch{}
  try{
    const b:any=await request.post('/building/queryByPage',{pageNo:1,pageSize:200,data:{}})
    const bm:Record<string,any>={}
    for(const x of (b.data.list||[])) bm[x.building_id]=x
    buildingMap.value=bm
  }catch{}
  try{
    const p:any=await request.post('/dormPublish/queryByPage',{pageNo:1,pageSize:50,data:{}})
    publishList.value=p.data.list||[]
  }catch{}
}
async function loadRooms(){
  const data:any={checkPublish:1}
  if(selectedCollege.value) data.collegeId=selectedCollege.value
  const res:any=await request.post('/dorm/queryByPage', {pageNo:1,pageSize:24,data})
  rooms.value=res.data.list||[]
  try{
    const p:any=await request.post('/dormPublish/queryByPage',{pageNo:1,pageSize:50,data:{}})
    publishList.value=p.data.list||[]
  }catch{}
}
async function doAssign(){
  if(!selected.value) return
  try{
    await request.post('/dorm/assign', {studentId:sid, buildingId:selected.value.building_id, roomId:selected.value.room_id, bedNo:1})
    ElMessage.success('选宿舍成功'); assign.value={building_id:selected.value.building_id, room_id:selected.value.room_id, bed_no:1}; loadRooms()
  }catch(e:any){ ElMessage.error(e?.message || e?.response?.data?.message || '选房失败，可能未发布或已截止') }
}
async function doExchange(){
  try{
    await request.post('/dorm/exchange', {studentId:sid, buildingId:selected.value.building_id, roomId:selected.value.room_id, bedNo:1})
    ElMessage.success('调宿成功'); assign.value={building_id:selected.value.building_id, room_id:selected.value.room_id, bed_no:1}
  }catch(e:any){ ElMessage.error(e?.message || e?.response?.data?.message || '调宿失败，可能未发布或已截止') }
}
async function doCheckout(){ await request.post('/dorm/checkout', {studentId:sid}); ElMessage.success('已退宿'); assign.value=null; loadRooms() }
onMounted(async()=>{ await loadMeta(); await loadRooms() })
</script>
<style scoped>
.dorm-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:10px}
.dorm-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px;cursor:pointer;transition:.2s}
.dorm-card:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(30,94,255,.12)}
.dorm-card.selected{border-color:#1e5eff;box-shadow:0 8px 20px rgba(30,94,255,.18)}
.dorm-card.full{opacity:.6}
.dorm-head{display:flex;justify-content:space-between;align-items:center;font-weight:700}
.room-no{font-size:14px}
.occupy{font-size:12px;padding:2px 8px;border-radius:999px;background:#eef3ff;color:#1e5eff}
.occupy.danger{background:#ffebe6;color:#ff4d4f}
</style>
