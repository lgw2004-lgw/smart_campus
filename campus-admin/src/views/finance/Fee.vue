<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>缴费管理 · 模拟微信Native（计费→下单→出码→轮询→确认）</h3>
      <el-button type="primary" @click="fetch">刷新订单</el-button>
    </div>

    <el-card style="margin-bottom:16px" shadow="never">
      <h4>1. 选课计费</h4>
      <el-form inline>
        <el-form-item label="学号"><el-input v-model="calcForm.studentId" placeholder="20240101" style="width:140px"/></el-form-item>
        <el-form-item label="选课ID(逗号)"><el-input v-model="calcForm.enrollIdsStr" placeholder="ENR...,ENR..." style="width:340px"/></el-form-item>
        <el-form-item><el-button @click="doCalc">计费</el-button> <el-button type="primary" @click="doPayMsg">生成订单</el-button></el-form-item>
      </el-form>
      <div v-if="calcData" style="margin-top:8px">
        <el-tag type="info">总额 {{ calcData.totalAmount }} 元</el-tag>
        <div style="margin-top:6px" v-for="it in calcData.items" :key="it.enrollId">{{ it.itemName }} ({{ it.courseId }}) 单价 {{ it.itemPrice }}</div>
      </div>
    </el-card>

    <el-card style="margin-bottom:16px" shadow="never">
      <h4>2. 支付</h4>
      <el-form inline>
        <el-form-item label="订单号"><el-input v-model="payForm.orderId" placeholder="ORD..." style="width:240px"/></el-form-item>
        <el-form-item><el-button type="warning" @click="getQR">获取二维码</el-button><el-button @click="pollStatus">轮询状态</el-button><el-button type="success" @click="confirmPay">确认已付</el-button></el-form-item>
      </el-form>
      <div v-if="qrData" style="text-align:center;margin-top:12px">
        <div>微信URL：{{ qrData.codeUrl }}</div>
        <img :src="qrData.qrCode" style="width:220px;height:220px;border:1px solid #eee;margin-top:8px"/>
        <div style="margin-top:8px"><el-tag :type="payStatus==='3'?'success':payStatus==='0'?'warning':'info'">状态 {{ payStatus==='3'?'已付':'未付(' + payStatus + ')' }}</el-tag></div>
      </div>
    </el-card>

    <el-card style="margin-bottom:16px" shadow="never">
      <h4>3. 退费</h4>
      <el-form inline>
        <el-form-item label="订单号"><el-input v-model="refundForm.orderId" placeholder="ORD..." style="width:240px"/></el-form-item>
        <el-form-item label="金额"><el-input v-model="refundForm.amount" placeholder="留空全退" style="width:120px"/></el-form-item>
        <el-form-item label="原因"><el-input v-model="refundForm.reason" style="width:200px"/></el-form-item>
        <el-form-item><el-button type="danger" @click="doRefund">退费</el-button></el-form-item>
      </el-form>
    </el-card>

    <h4>订单列表</h4>
    <el-form inline style="margin-bottom:8px">
      <el-form-item><el-input v-model="query.studentId" placeholder="学号" clearable style="width:140px"/><el-select v-model="query.orderStatus" placeholder="状态" clearable style="width:120px;margin-left:6px"><el-option label="未付" value="0"/><el-option label="已付" value="3"/></el-select><el-button style="margin-left:6px" @click="search">查询</el-button></el-form-item>
    </el-form>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="order_id" label="订单ID" width="190"/>
      <el-table-column prop="student_id" label="学号" width="110"/>
      <el-table-column prop="order_amount" label="金额" width="100"/>
      <el-table-column prop="order_status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.order_status==='3'?'success':'warning'">{{ row.order_status==='3'?'已付':'未付' }}</el-tag></template></el-table-column>
      <el-table-column prop="ch_id" label="关联选课" min-width="200"/>
      <el-table-column prop="create_time" label="创建时间" width="170"/>
      <el-table-column label="操作" width="220"><template #default="{row}"><el-button size="small" @click="payForm.orderId=row.order_id;refundForm.orderId=row.order_id">选中</el-button><el-button size="small" @click="getQRById(row.order_id)">二维码</el-button></template></el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" :page-sizes="[10,20,50]" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange" />
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/feeOrder/queryByPage', {studentId:'', orderStatus:''})
fetch()
const calcForm=reactive<any>({studentId:'20240101', enrollIdsStr:''})
const calcData=ref<any>(null)
async function doCalc(){ const ids=calcForm.enrollIdsStr.split(',').map((s:string)=>s.trim()).filter(Boolean); if(!ids.length) return ElMessage.warning('填选课ID'); const res:any = await request.post('/fee/calc', {enrollIds:ids}); calcData.value=res.data; ElMessage.success('计费完成') }
async function doPayMsg(){ const ids=calcForm.enrollIdsStr.split(',').map((s:string)=>s.trim()).filter(Boolean); const res:any = await request.post('/fee/payMsg', {studentId:calcForm.studentId, enrollIds:ids}); ElMessage.success(`订单 ${res.data.orderId} 已生成`); payForm.orderId=res.data.orderId; refundForm.orderId=res.data.orderId; fetch() }

const payForm=reactive<any>({orderId:''})
const qrData=ref<any>(null); const payStatus=ref('')
async function getQR(){ if(!payForm.orderId) return ElMessage.warning('填订单号'); const res:any = await request.post(`/weChatPay/getNativeCodeUrl/${payForm.orderId}`); qrData.value=res.data; ElMessage.success('二维码已生成'); pollStatus() }
async function getQRById(id:string){ payForm.orderId=id; await getQR() }
let timer:any=null
async function pollStatus(){ if(!payForm.orderId) return; const res:any = await request.get(`/weChatPay/getPayStatus/${payForm.orderId}`); payStatus.value=res.data.orderStatus; if(payStatus.value!=='3'){ clearTimeout(timer); timer=setTimeout(pollStatus,1500); ElMessage.info('轮询中...未付') } else { ElMessage.success('已支付') } }
async function confirmPay(){ await request.post(`/feeOrder/updateById/${payForm.orderId}`); ElMessage.success('已确认支付，选课已生效'); payStatus.value='3'; fetch() }

const refundForm=reactive<any>({orderId:'', amount:'', reason:''})
async function doRefund(){ await request.post('/fee/refund', {orderId:refundForm.orderId, refundAmount:refundForm.amount?Number(refundForm.amount):undefined, reason:refundForm.reason}); ElMessage.success('退费完成，已联动退选'); fetch() }
</script>
