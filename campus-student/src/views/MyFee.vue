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

    <el-card shadow="never" style="border-radius:14px;margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><h3 style="margin:0">一卡通（充值/消费）</h3><el-button size="small" @click="loadCard">刷新</el-button></div>
      <div style="display:flex;gap:16px;align-items:center;background:#f6f8ff;border:1px solid #d6e4ff;border-radius:12px;padding:12px;flex-wrap:wrap">
        <div><div style="font-size:12px;color:#8a94a6">卡内余额</div><div style="font-size:26px;font-weight:800;color:#1e5eff">¥{{ cardBalance }}</div></div>
        <el-button type="success" @click="recharge(50)">充 50</el-button>
        <el-button type="success" @click="recharge(100)">充 100</el-button>
        <el-button type="warning" @click="consume('食堂')">食堂消费 ¥12</el-button>
        <el-button type="warning" @click="consume('超市')">超市消费 ¥25.5</el-button>
      </div>
      <el-table :data="cardTx" size="small" border style="margin-top:10px" max-height="240">
        <el-table-column label="类型" width="80"><template #default="{row}"><el-tag size="small" :type="row.tx_type==='1'?'success':'danger'">{{ row.tx_type==='1'?'充值':'消费' }}</el-tag></template></el-table-column>
        <el-table-column label="金额" width="90"><template #default="{row}">¥{{ row.amount }}</template></el-table-column>
        <el-table-column prop="balance_after" label="余额" width="90"/>
        <el-table-column prop="scene" label="场景" width="90"/>
        <el-table-column prop="create_time" label="时间"/>
      </el-table>
    </el-card>

    <el-dialog v-model="qrDialog" title="微信扫码支付（模拟）" width="420" center @close="cancelQrTimer">
      <div v-if="qr" style="text-align:center">
        <img :src="qr.qrCode" @click="onQrClick" :style="{width:'220px',height:'220px',border:'1px solid #eee',borderRadius:'12px',cursor: qrPaying?'wait':'pointer', opacity: qrPaying?0.7:1}" title="点击二维码 5秒后自动支付成功"/>
        <div style="margin-top:8px;font-size:12px;color:#1e5eff">点击二维码 5秒后自动支付成功{{ qrPaying ? `（${qrCountdown}s）` : '' }}</div>
        <div style="margin-top:4px;word-break:break-all;font-size:12px;color:#666">{{ qr.codeUrl }}</div>
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
const qr=ref<any>(null); const qrDialog=ref(false); const qrOrder=ref<any>(null); const qrPaying=ref(false); const qrCountdown=ref(5)
let qrTimer:any=null; let qrCountTimer:any=null
async function showQR(row:any){ const res:any=await request.post(`/weChatPay/getNativeCodeUrl/${row.order_id}`); qr.value=res?.data ?? null; qrOrder.value=row; qrPaying.value=false; qrCountdown.value=5; qrDialog.value=true }
function cancelQrTimer(){ if(qrTimer) clearTimeout(qrTimer); if(qrCountTimer) clearInterval(qrCountTimer); qrTimer=null; qrCountTimer=null; qrPaying.value=false }
async function onQrClick(){
  if(!qrOrder.value || qrPaying.value) return
  qrPaying.value=true; qrCountdown.value=5
  ElMessage.info('已点击二维码，5秒后自动支付成功')
  qrCountTimer=setInterval(()=>{ if(qrCountdown.value>1) qrCountdown.value--; else clearInterval(qrCountTimer) }, 1000)
  qrTimer=setTimeout(async()=>{
    try{ await request.post(`/feeOrder/updateById/${qrOrder.value.order_id}`); ElMessage.success('支付成功'); qrDialog.value=false; cancelQrTimer(); loadOrders(); loadTuition() }catch{ qrPaying.value=false; if(qrCountTimer) clearInterval(qrCountTimer) }
  }, 5000)
}
async function confirm(row:any){ await request.post(`/feeOrder/updateById/${row.order_id}`); ElMessage.success('支付成功'); loadOrders(); loadTuition() }
// ---- 一卡通 ----
const cardBalance=ref('0.00'); const cardTx=ref<any[]>([])
async function loadCard(){
  try{
    const r:any=await request.get('/card/account',{params:{studentId:sid}}); cardBalance.value=Number(r.data.balance).toFixed(2)
    const r2:any=await request.post('/card/tx/queryByPage',{pageNo:1,pageSize:10,data:{studentId:sid}}); cardTx.value=r2.data.list||[]
  }catch{}
}
async function recharge(amount:number){
  const r:any=await request.post('/card/recharge', {studentId:sid, amount})
  ElMessage.success(`充值成功，余额 ¥${r.data.balance}`); loadCard()
}
async function consume(scene:string){
  const amount = scene==='食堂'?12:25.5
  try{
    const r:any=await request.post('/card/consume', {studentId:sid, amount, scene})
    ElMessage.success(`${scene}消费 ¥${amount}，余额 ¥${r.data.balance}`); loadCard()
  }catch{}
}
onMounted(()=>{ loadTuition(); loadOrders(); loadCard() })
</script>
<style scoped>
.order-list{margin-top:12px;display:flex;flex-direction:column;gap:10px}
.order-card{background:#fff;border:1px solid #e6ebf5;border-radius:12px;padding:12px}
.order-head{display:flex;justify-content:space-between;align-items:center}
</style>
