<template>
  <div>
    <el-card shadow="never" style="border-radius:14px;margin-bottom:14px">
      <h3 style="margin:0 0 12px">我的待缴费</h3>
      <div v-if="!enrolls.length" style="color:#8a94a6;font-size:13px">暂无待缴费选课</div>
      <div v-else>
        <div class="fee-item" v-for="e in enrolls" :key="e.enroll_id">
          <div><div style="font-weight:600">{{ courseMap[e.course_id] || e.course_id }}</div><div style="font-size:12px;color:#8a94a6">{{ e.enroll_id }}</div></div>
          <el-tag type="warning" effect="plain">待缴费</el-tag>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px;background:#fff7e6;border:1px solid #ffe7ba;padding:10px;border-radius:10px">
          <div>已选 {{ enrolls.length }} 门 · 计费按学分 <b style="color:#ff7e00">{{ calcData?.totalAmount||'—' }} 元</b></div>
          <div style="display:flex;gap:8px"><el-button @click="calc">计费</el-button><el-button type="primary" @click="payMsg">生成缴费单</el-button></div>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" style="border-radius:14px">
      <div style="display:flex;justify-content:space-between;align-items:center"><h3 style="margin:0">我的订单</h3><el-button size="small" @click="loadOrders">刷新</el-button></div>
      <div class="order-list">
        <div class="order-card" v-for="o in orders" :key="o.order_id">
          <div class="order-head"><span style="font-weight:700">{{ o.order_id }}</span><el-tag :type="o.order_status==='3'?'success':'warning'" effect="plain">{{ o.order_status==='3'?'已付':'未付' }}</el-tag></div>
          <div style="font-size:12px;color:#8a94a6">金额 ¥{{ o.order_amount }} · {{ o.create_time?.slice(0,19) }}</div>
          <div style="font-size:12px;color:#8a94a6;word-break:break-all">关联 {{ o.ch_id }}</div>
          <div style="margin-top:8px;display:flex;gap:8px">
            <el-button size="small" @click="showQR(o)">二维码</el-button>
            <el-button size="small" @click="poll(o)">轮询</el-button>
            <el-button size="small" type="success" @click="confirm(o)" :disabled="o.order_status==='3'">我已支付</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="qrDialog" title="微信扫码支付（模拟）" width="420" center>
      <div v-if="qr" style="text-align:center">
        <img :src="qr.qrCode" style="width:220px;height:220px;border:1px solid #eee;border-radius:12px"/>
        <div style="margin-top:8px;word-break:break-all;font-size:12px;color:#666">{{ qr.codeUrl }}</div>
        <div style="margin-top:8px"><el-tag :type="status==='3'?'success':'warning'">当前 {{ status==='3'?'已付':'未付' }}</el-tag></div>
        <div style="margin-top:8px;color:#8a94a6;font-size:12px">后台“财务管理·缴费”也可看到此订单联动</div>
      </div>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const enrolls=ref<any[]>([]); const calcData=ref<any>(null)
const courseMap=ref<Record<string,string>>({})
async function loadCourseMap(){ const res:any=await request.post('/course/queryByPage', {pageNo:1,pageSize:200,data:{}}); const m:Record<string,string>={}; for(const c of (res.data.list||[])) m[c.course_id]=c.course_name; courseMap.value=m }
async function loadEnroll(){ const res:any=await request.post('/enrollment/queryByPage', {pageNo:1,pageSize:20,data:{studentId:sid,status:'0'}}); enrolls.value=res.data.list||[] }
async function calc(){ const ids=enrolls.value.map(v=>v.enroll_id); const res:any=await request.post('/fee/calc', {enrollIds:ids}); calcData.value=res.data; ElMessage.success('计费完成') }
async function payMsg(){ const ids=enrolls.value.map(v=>v.enroll_id); const res:any=await request.post('/fee/payMsg', {studentId:sid, enrollIds:ids}); ElMessage.success(`订单 ${res.data.orderId}`); loadOrders() }
const orders=ref<any[]>([])
async function loadOrders(){ const res:any=await request.post('/feeOrder/queryByPage', {pageNo:1,pageSize:20,data:{studentId:sid}}); orders.value=res.data.list||[] }
const qr=ref<any>(null); const status=ref(''); const qrDialog=ref(false)
async function showQR(row:any){ const res:any=await request.post(`/weChatPay/getNativeCodeUrl/${row.order_id}`); qr.value=res.data; status.value=row.order_status; qrDialog.value=true }
async function poll(row:any){ const res:any=await request.get(`/weChatPay/getPayStatus/${row.order_id}`); status.value=res.data.orderStatus; ElMessage.info(`状态 ${status.value}`) }
async function confirm(row:any){ await request.post(`/feeOrder/updateById/${row.order_id}`); ElMessage.success('支付成功，选课已生效'); loadOrders(); loadEnroll() }
onMounted(()=>{ loadCourseMap(); loadEnroll(); loadOrders() })
</script>
<style scoped>
.fee-item{display:flex;justify-content:space-between;align-items:center;padding:10px;border:1px solid #e6ebf5;border-radius:10px;margin-bottom:8px;background:#fff}
.order-list{margin-top:12px;display:flex;flex-direction:column;gap:10px}
.order-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px}
.order-head{display:flex;justify-content:space-between;align-items:center}
</style>
