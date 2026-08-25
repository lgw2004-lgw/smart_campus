<template>
  <div v-loading="loading">
    <el-row :gutter="16">
      <el-col :span="6" v-for="c in cards" :key="c.title">
        <el-card shadow="never" style="border-radius:12px">
          <div style="font-size:13px;color:#8a94a6">{{ c.title }}</div>
          <div style="font-size:28px;font-weight:800;margin-top:6px">{{ c.value }}<span v-if="c.unit" style="font-size:14px;font-weight:400;color:#8a94a6"> {{ c.unit }}</span></div>
          <div style="font-size:12px;color:#999;margin-top:4px">{{ c.sub }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">选课热度 Top10</div></template>
          <div ref="chartRef" style="height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">成绩分布</div></template>
          <div ref="pieRef" style="height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="8">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">缴费率</div></template>
          <div ref="feeRef" style="height:240px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">图书借阅趋势（近7天）</div></template>
          <div ref="trendRef" style="height:240px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">宿舍入住率（按楼栋）</div></template>
          <div v-for="r in dormOcc" :key="r.building" style="display:flex;align-items:center;gap:10px;margin:10px 0">
            <div style="width:70px;font-size:13px">{{ r.building }}</div>
            <el-progress :percentage="r.rate" :stroke-width="12" style="flex:1" :color="r.rate>=95?'#ff4d4f':'#1e5eff'"/>
            <span style="font-size:12px;color:#666">{{ r.rate }}%</span>
          </div>
          <el-empty v-if="!dormOcc.length" description="暂无数据" :image-size="50"/>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref, reactive } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'

const loading=ref(false)
const cards=reactive<any[]>([
  {title:'在校学生', value:'—', sub:'在读学生总数'},
  {title:'有效选课', value:'—', sub:'未退选记录'},
  {title:'待缴费订单', value:'—', sub:'未支付缴费单'},
  {title:'图书在借', value:'—', sub:'未归还图书'},
  {title:'缴费率', value:'—', unit:'%', sub:'已支付订单占比'},
  {title:'未处理预警', value:'—', sub:'挂科/学分预警'},
  {title:'补考报名', value:'—', sub:'有效报名数'},
  {title:'评教均分', value:'—', unit:'/5', sub:'全校课程平均'},
])
const chartRef=ref<HTMLDivElement>(); const pieRef=ref<HTMLDivElement>()
const feeRef=ref<HTMLDivElement>(); const trendRef=ref<HTMLDivElement>()
const dormOcc=ref<any[]>([])

async function load(){
  loading.value=true
  try{
    const res:any = await request.get('/stats/dashboard')
    const d = res?.data ?? {}
    const c = d.cards ?? {}
    cards[0].value=c.students??0; cards[1].value=c.enrollments??0; cards[2].value=c.unpaidOrders??0
    cards[3].value=c.borrowing??0; cards[4].value=c.feeRate??0; cards[5].value=c.warnings??0
    cards[6].value=c.examSignups??0; cards[7].value=c.avgRating??0

    echarts.init(chartRef.value!).setOption({
      tooltip:{trigger:'axis'}, grid:{bottom:70, left:40},
      xAxis:{type:'category', data:(d.enrollTop??[]).map((w:any)=>w.name), axisLabel:{interval:0, rotate:35, fontSize:10}},
      yAxis:{type:'value'},
      series:[{type:'bar', data:(d.enrollTop??[]).map((w:any)=>w.value), itemStyle:{color:'#1e5eff'}, barMaxWidth:32}]
    })
    echarts.init(pieRef.value!).setOption({
      tooltip:{trigger:'item'},
      series:[{type:'pie', radius:['0%','62%'], data:Object.entries(d.scoreBuckets??{}).map(([k,v])=>({name:k,value:v})), label:{formatter:'{b}: {c}'}}]
    })
    const feeChart = echarts.init(feeRef.value!)
    feeChart.setOption({
      tooltip:{trigger:'item'},
      series:[{type:'pie', radius:['45%','68%'], center:['50%','52%'],
        data:(d.feeDonut??[]) as any[], label:{formatter:'{b}: {c} ({d}%)'}}]
    })
    echarts.init(trendRef.value!).setOption({
      tooltip:{trigger:'axis'}, grid:{left:36, bottom:30},
      xAxis:{type:'category', data:(d.borrowTrend??[]).map((t:any)=>t.date)},
      yAxis:{type:'value', minInterval:1},
      series:[{type:'line', smooth:true, areaStyle:{opacity:.15}, data:(d.borrowTrend??[]).map((t:any)=>t.cnt), itemStyle:{color:'#7c3aed'}}]
    })
    dormOcc.value=d.dormOccupancy??[]
  } finally{ loading.value=false }
}
onMounted(load)
</script>
