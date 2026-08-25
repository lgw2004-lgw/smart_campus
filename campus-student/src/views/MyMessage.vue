<template>
  <div>
    <div class="page-head"><div><h2>消息中心</h2><p>学校推送给我的站内消息</p></div></div>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-weight:700">全部消息</span><el-tag type="danger">未读 {{ unread }}</el-tag></div></template>
      <div v-for="m in list" :key="m.messageId" class="msg" :class="{unread:!m.read}" @click="read(m)">
        <div class="dot"></div>
        <div style="flex:1;min-width:0">
          <div class="t"><el-tag size="small" :type="tagType(m.msgType)" effect="plain" style="margin-right:6px">{{ tagText(m.msgType) }}</el-tag>{{ m.title }}</div>
          <div class="c">{{ m.content }}</div>
        </div>
        <div class="time">{{ m.createTime?.slice(0,19) }}</div>
      </div>
      <el-empty v-if="!list.length" description="暂无消息"/>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
const sid=localStorage.getItem('studentId')||''
const list=ref<any[]>([]); const unread=ref(0)
async function load(){
  const r:any=await request.post('/message/queryMine', {studentId:sid})
  list.value=r.data.list||[]; unread.value=r.data.unread||0
}
async function read(m:any){
  if(!m.read){ await request.post('/message/read', {messageId:m.messageId, studentId:sid}); m.read=true; unread.value=Math.max(0,unread.value-1) }
}
function tagType(t:string){ return {'SCORE':'success','EXAM':'warning','FEE':'danger','DORM':'primary'}[t]||'info' }
function tagText(t:string){ return {'SCORE':'成绩','EXAM':'考试','FEE':'缴费','DORM':'宿舍'}[t]||'系统' }
onMounted(load)
</script>
<style scoped>
.page-head{margin-bottom:12px}
.page-head h2{margin:0}
.page-head p{margin:4px 0 0;color:#8a94a6;font-size:13px}
.msg{display:flex;gap:10px;align-items:center;padding:12px;border-bottom:1px solid #f0f2f5;cursor:pointer;border-radius:8px}
.msg:hover{background:#f6f8ff}
.msg.unread .t{font-weight:800}
.dot{width:8px;height:8px;background:#1e5eff;border-radius:50%;opacity:.3;flex-shrink:0}
.unread .dot{opacity:1;background:#ff4d4f}
.t{font-size:14px;font-weight:600}
.c{font-size:13px;color:#666;margin-top:2px}
.time{font-size:12px;color:#8a94a6;flex-shrink:0}
</style>
