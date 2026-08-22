<template>
  <div>
    <el-carousel v-if="banners.length" height="180px" style="border-radius:14px;overflow:hidden;margin-bottom:14px"><el-carousel-item v-for="b in banners" :key="b.id"><img :src="b.url" style="width:100%;height:180px;object-fit:cover"/><div class="banner-title">{{ b.name }}</div></el-carousel-item></el-carousel>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><div style="font-weight:700">校园公告 · 与管理端内容管理联动</div></template>
      <div v-for="n in notices" :key="n.notice_id" class="notice-card">
        <div class="notice-tag">{{ n.notice_type==='2'?'公告':'通知' }}</div>
        <div style="flex:1"><div class="notice-title">{{ n.notice_title }}</div><div class="notice-content">{{ n.notice_content }}</div><div class="notice-time">{{ n.create_time?.slice(0,19) }}</div></div>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
const banners=ref<any[]>([]); const notices=ref<any[]>([])
onMounted(async()=>{
  const r:any=await request.get('/banner/loadBanner'); banners.value=r.data||[]
  const r2:any=await request.post('/notice/queryByPage', {pageNo:1,pageSize:20,data:{}}); notices.value=r2.data.list||[]
})
</script>
<style scoped>
.banner-title{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(0,0,0,.6));color:#fff;padding:10px;font-size:14px}
.notice-card{display:flex;gap:12px;padding:12px;border:1px solid #e6ebf5;border-radius:12px;margin-bottom:10px;background:#fff}
.notice-tag{width:48px;height:48px;background:#eef3ff;color:#1e5eff;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0}
.notice-title{font-weight:700}
.notice-content{font-size:13px;color:#4a5a6e;margin-top:4px}
.notice-time{font-size:12px;color:#8a94a6;margin-top:4px}
</style>
