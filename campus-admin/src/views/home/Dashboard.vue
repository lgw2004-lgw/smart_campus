<template>
  <div v-loading="loading">
    <el-row :gutter="16">
      <el-col :span="6" v-for="c in cards" :key="c.title">
        <el-card shadow="never" style="border-radius:12px">
          <div style="font-size:13px;color:#8a94a6">{{ c.title }}</div>
          <div style="font-size:28px;font-weight:800;margin-top:6px">{{ c.value }}</div>
          <div style="font-size:12px;color:#999;margin-top:4px">{{ c.sub }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">选课人数</div></template>
          <div ref="chartRef" style="height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">成绩分布</div></template>
          <div ref="pieRef" style="height:280px"></div>
          <div v-if="rank" style="font-size:13px;color:#666;margin-top:8px">平均分 {{ rank.avg.toFixed(1) }} · 总数 {{ rank.total }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">宿舍入住率</div></template>
          <div v-for="r in dormStats" :key="r.room_id" style="display:flex;align-items:center;gap:10px;margin:8px 0">
            <div style="width:120px;font-size:13px">{{ r.building_id }}栋 {{ r.room_no }}</div>
            <el-progress :percentage="Math.round(r.occupied/r.capacity*100)" :stroke-width="10" style="flex:1" :color="r.occupied>=r.capacity?'#ff4d4f':'#1e5eff'"/>
            <span style="font-size:12px;color:#666">{{ r.occupied }}/{{ r.capacity }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" style="border-radius:12px">
          <template #header><div style="font-weight:700">图书借阅排行</div></template>
          <div v-for="b in borrowTop" :key="b.book_id" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f0f2f5">
            <span style="font-size:13px">{{ b.book_name }}</span><el-tag size="small" type="info">{{ b.stock }}/{{ b.total }} 可借</el-tag>
          </div>
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
const cards=reactive([
  {title:'在校学生', value:'—', sub:'在读学生总数'},
  {title:'今日选课(总)', value:'—', sub:'选课记录总数'},
  {title:'待缴费订单', value:'—', sub:'未支付缴费单'},
  {title:'图书在借', value:'—', sub:'未归还图书'},
])
const chartRef=ref<HTMLDivElement>()
const pieRef=ref<HTMLDivElement>()
const rank=ref<any>(null)
const dormStats=ref<any[]>([])
const borrowTop=ref<any[]>([])

async function load(){
  loading.value=true
  try{
    const [stuRes, enrollRes, feeRes, borrowRes, workNumRes, rankRes, dormRes, bookRes, courseRes] = await Promise.all([
      request.post('/student/queryByPage', {pageNo:1,pageSize:1,data:{}}),
      request.post('/enrollment/queryByPage', {pageNo:1,pageSize:1,data:{}}),
      request.post('/feeOrder/queryByPage', {pageNo:1,pageSize:1,data:{orderStatus:'0'}}),
      request.post('/borrow/queryByPage', {pageNo:1,pageSize:1,data:{status:'0'}}),
      request.post('/enrollment/queryWorkNum', {}),
      request.post('/score/queryRank', {}),
      request.post('/dorm/queryByPage', {pageNo:1,pageSize:5,data:{}}),
      request.post('/book/queryByPage', {pageNo:1,pageSize:5,data:{}}),
      request.post('/course/queryByPage', {pageNo:1,pageSize:200,data:{}}),
    ])
    const courseMap:Record<string,string>={}; for(const c of (courseRes.data.list||[])) courseMap[c.course_id]=c.course_name
    cards[0].value = String(stuRes.data.total)
    cards[1].value = String(enrollRes.data.total)
    cards[2].value = String(feeRes.data.total)
    cards[3].value = String(borrowRes.data.total)
    rank.value = rankRes.data

    // 选课柱状（后端联表直接返回课程名）
    const work = workNumRes.data as any[]
    const chart = echarts.init(chartRef.value!)
    chart.setOption({
      tooltip:{trigger:'axis'},
      grid:{bottom:60},
      xAxis:{type:'category', data: work.map(w=>w.courseName), axisLabel:{interval:0, rotate:30}},
      yAxis:{type:'value'},
      series:[{type:'bar', data: work.map(w=>w.cnt), itemStyle:{color:'#1e5eff'}}]
    })

    // 成绩饼图
    const pie = echarts.init(pieRef.value!)
    const buckets = rankRes.data.buckets || {}
    pie.setOption({
      tooltip:{trigger:'item'},
      series:[{type:'pie', radius:'60%', data: Object.entries(buckets).map(([k,v])=>({name:k, value:v})), label:{formatter:'{b}: {c}'} }]
    })

    dormStats.value = dormRes.data.list || []
    borrowTop.value = bookRes.data.list || []
  } finally{ loading.value=false }
}
onMounted(load)
</script>
