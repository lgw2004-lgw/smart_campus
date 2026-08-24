<template>
  <div>
    <el-card shadow="never" style="border-radius:14px;margin-bottom:14px">
      <h3 style="margin:0 0 12px">总学费（开学一次）</h3>
      <div v-if="!tuition" style="color:#8a94a6">加载中...</div>
      <div v-else>
        <div style="display:flex;justify-content:space-between;align-items:center;background:#f0f7ff;border:1px solid #d6e4ff;padding:12px;border-radius:10px">
          <div>
            <div style="font-weight:700">{{ tuition.semester }} · ¥{{ tuition.totalAmount }}</div>
            <div style="font-size:12px;color:#666;margin-top:4px">{{ tuition.detail }}</div>
          </div>
          <div v-if="tuitionPaid" style="color:#52c41a;font-weight:600">✓ 已缴总学费，可直接选课</div>
          <el-button v-else type="primary" @click="payTuition">缴纳总学费 ¥{{ tuition.totalAmount }}</el-button>
        </div>
        <div v-if="tuitionOrder" style="margin-top:10px;font-size:12px;color:#8a94a6">订单 {{ tuitionOrder.order_id }} · <el-tag :type="tuitionOrder.order_status==='3'?'success':'warning'">{{ tuitionOrder.order_status==='3'?'已付':'待付' }}</el-tag> <el-button size="small" @click="payTuitionOrder">去支付</el-button></div>
      </div>
    </el-card>

    <el-card shadow="never" style="border-radius:14px;margin-bottom:14px">
      <h3 style="margin:0 0 12px">重修费（按学分计费 · 选完重修课自动计算）</h3>
      <div v-if="retakeOrders.length===0" style="color:#8a94a6;font-size:13px">暂无重修订单（选重修课后自动生成，按学分×100）</div>
      <div v-else>
        <div class="order-card" v-for="o in retakeOrders" :key="o.order_id" style="margin-bottom:8px">
          <div style="display:flex;justify-content:space-between"><span style="font-weight:600">{{ o.detail || o.ch_id }}</span><el-tag :type="o.order_status==='3'?'success':'warning'">{{ o.order_status==='3'?'已付':'待付' }}</el-tag></div>
          <div style="font-size:12px;color:#666">金额 ¥{{ o.order_amount }} · {{ o.semester }} · {{ o.create_time?.slice(0,19) }}</div>
          <div style="margin-top:6px"><el-button size="small" @click="showQR(o)">二维码</el-button><el-button size="small" type="success" @click="confirm(o)" :disabled="o.order_status==='3'">我已支付</el-button></div>
        </div>
      </div>
    </el-card>

    <el-card shadow="never" style="border-radius:14px">
      <div style="display:flex;justify-content:space-between;align-items:center"><h3 style="margin:0">我的订单（总学费/重修）</h3><el-button size="small" @click="loadOrders">刷新</el-button></div>
      <div class="order-list">
        <div class="order-card" v-for="o in orders" :key="o.order_id">
          <div class="order-head"><span style="font-weight:700">{{ o.order_id }} <el-tag size="small" style="margin-left:6px">{{ o.order_type==='TUITION'?'总学费':o.order_type==='RETAKE'?'重修':'普通' }}</el-tag></span><el-tag :type="o.order_status==='3'?'success':'warning'" effect="plain">{{ o.order_status==='3'?'已付':'未付' }}</el-tag></div>
          <div style="font-size:12px;color:#8a94a6">金额 ¥{{ o.order_amount }} · {{ o.semester||'-' }} · {{ o.create_time?.slice(0,19) }}</div>
          <div style="font-size:12px;color:#8a94a6;word-break:break-all" v-if="o.detail">明细：{{ o.detail }}</div>
          <div style="margin-top:8px;display:flex;gap:8px">
            <el-button size="small" @click="showQR(o)">二维码</el-button>
            <el-button size="small" type="success" @click="confirm(o)" :disabled="o.order_status==='3'">我已支付</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="qrDialog" title="微信扫码支付（模拟）" width="420" center>
      <div v-if="qr" style="text-align:center">
        <img :src="qr.qrCode" style="width:220px;height:220px;border:1px solid #eee;border-radius:12px"/>
        <div style="margin-top:8px;word-break:break-all;font-size:12px;color:#666">{{ qr.codeUrl }}</div>
      </div>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const sid=localStorage.getItem('studentId')||''
const tuition=ref<any>(null); const tuitionPaid=ref(false); const tuitionOrder=ref<any>(null)
async function loadTuition(){
  try{ const res:any=await request.get('/fee/tuition/get'); tuition.value=res?.data ?? null }catch{ tuition.value=null }
  if(tuition.value){
    const res2:any=await request.post('/feeOrder/queryByPage', {pageNo:1,pageSize:5,data:{studentId:sid}})
    const lst=res2?.data?.list ?? []
    const t=lst.find((o:any)=>o.order_type==='TUITION' && o.semester===tuition.value.semester)
    tuitionOrder.value=t||null
    tuitionPaid.value=!!lst.find((o:any)=>o.order_type==='TUITION' && o.semester===tuition.value.semester && o.order_status==='3')
  }
}
async function payTuition(){
  if(!tuition.value) return
  const res:any=await request.post('/fee/tuition/pay', {studentId:sid, semester:tuition.value.semester})
  if(res?.data?.orderId) ElMessage.success(`总学费订单 ${res.data.orderId} 已生成，请支付`); loadOrders(); loadTuition()
}
async function payTuitionOrder(){ if(!tuitionOrder.value) return payTuition(); showQR(tuitionOrder.value) }
const orders=ref<any[]>([]); const retakeOrders=ref<any[]>([])
async function loadOrders(){
  const res:any=await request.post('/feeOrder/queryByPage', {pageNo:1,pageSize:20,data:{studentId:sid}})
  orders.value=res?.data?.list ?? []
  retakeOrders.value=orders.value.filter((o:any)=>o.order_type==='RETAKE')
}
const qr=ref<any>(null); const qrDialog=ref(false)
async function showQR(row:any){ const res:any=await request.post(`/weChatPay/getNativeCodeUrl/${row.order_id}`); qr.value=res?.data ?? null; qrDialog.value=true }
async function confirm(row:any){ await request.post(`/feeOrder/updateById/${row.order_id}`); ElMessage.success('支付成功'); loadOrders(); loadTuition() }
onMounted(()=>{ loadTuition(); loadOrders() })
</script>
<style scoped>
.order-list{margin-top:12px;display:flex;flex-direction:column;gap:10px}
.order-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px}
.order-head{display:flex;justify-content:space-between;align-items:center}
</style>
