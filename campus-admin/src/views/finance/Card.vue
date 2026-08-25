<template>
  <el-card>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <h3>一卡通账户 · 余额与充值/消费流水</h3>
      <div>
        <el-input v-model="query.studentId" placeholder="学号" clearable style="width:150px;margin-right:6px"/>
        <el-button type="primary" @click="search">查询</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" border>
      <el-table-column prop="student_id" label="学号" width="150"/>
      <el-table-column label="余额(¥)" width="130"><template #default="{row}"><span :style="{color:Number(row.balance)<10?'#e11d48':'#16a34a',fontWeight:700}">{{ Number(row.balance).toFixed(2) }}</span></template></el-table-column>
      <el-table-column prop="update_time" label="最近变动" width="170"/>
      <el-table-column label="操作" min-width="260">
        <template #default="{row}">
          <el-button size="small" type="success" @click="recharge(row)">充值</el-button>
          <el-button size="small" type="warning" @click="consume(row)">消费</el-button>
          <el-button size="small" @click="txs(row)">流水</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination style="margin-top:12px;justify-content:flex-end" v-model:current-page="pageNo" v-model:page-size="pageSize" :total="total" layout="total,sizes,prev,pager,next" @current-change="handleCurrentChange" @size-change="handleSizeChange"/>

    <el-dialog v-model="dlg" :title="mode==='recharge'?'账户充值':'模拟POS消费'" width="420">
      <el-form label-width="90px">
        <el-form-item label="学号"><el-input v-model="cur.student_id" disabled/></el-form-item>
        <el-form-item :label="mode==='recharge'?'充值金额':'消费金额'"><el-input-number v-model="amount" :min="0.1" :max="10000" :precision="2" style="width:100%"/></el-form-item>
        <el-form-item v-if="mode==='consume'" label="消费场景">
          <el-select v-model="scene" style="width:100%"><el-option v-for="s in ['食堂','超市','图书馆','医务室']" :key="s" :label="s" :value="s"/></el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg=false">取消</el-button><el-button type="primary" @click="submit">确认</el-button></template>
    </el-dialog>

    <el-dialog v-model="txDlg" title="交易流水" width="560">
      <el-table :data="txList" size="small" border max-height="380">
        <el-table-column prop="tx_id" label="流水号" width="140"/>
        <el-table-column label="类型" width="80"><template #default="{row}"><el-tag size="small" :type="row.tx_type==='1'?'success':row.tx_type==='2'?'danger':'info'">{{ ({'1':'充值','2':'消费','3':'退款'} as Record<string,string>)[row.tx_type] }}</el-tag></template></el-table-column>
        <el-table-column label="金额" width="90"><template #default="{row}">¥{{ row.amount }}</template></el-table-column>
        <el-table-column prop="balance_after" label="余额" width="90"/>
        <el-table-column prop="scene" label="场景"/>
      </el-table>
    </el-dialog>
  </el-card>
</template>
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { usePage } from '@/composables/usePage'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
const { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search } = usePage('/card/accounts/queryByPage', {studentId:''})
fetch()
const dlg=ref(false); const mode=ref('recharge'); const amount=ref(50); const scene=ref('食堂'); const cur=reactive<any>({})
function recharge(row:any){ Object.assign(cur,row); mode.value='recharge'; amount.value=50; dlg.value=true }
function consume(row:any){ Object.assign(cur,row); mode.value='consume'; amount.value=10; dlg.value=true }
async function submit(){
  const url = mode.value==='recharge'?'/card/recharge':'/card/consume'
  const body:any = {studentId:cur.student_id, amount:amount.value}
  if(mode.value==='consume') body.scene=scene.value
  try{ const r:any=await request.post(url, body); ElMessage.success(`成功，余额 ¥${r.data.balance}`); dlg.value=false; fetch() }catch{}
}
const txDlg=ref(false); const txList=ref<any[]>([])
async function txs(row:any){
  const r:any=await request.post('/card/tx/queryByPage', {pageNo:1,pageSize:50,data:{studentId:row.student_id}})
  txList.value=r.data.list||[]; txDlg.value=true
}
</script>
