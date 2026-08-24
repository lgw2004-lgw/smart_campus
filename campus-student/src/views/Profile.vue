<template>
  <div>
    <el-card shadow="never" style="border-radius:14px">
      <template #header><div style="font-weight:700">个人资料</div></template>
      <div v-loading="loading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学号">{{ data.student_id }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ data.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ data.sex==='1'?'女':'男' }}</el-descriptions-item>
          <el-descriptions-item label="身份证">{{ data.id_card }}</el-descriptions-item>
          <el-descriptions-item label="手机">{{ data.phone }}</el-descriptions-item>
          <el-descriptions-item label="学院">{{ data.college_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ data.major_name || data.dept_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ data.class_name || data.class_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="入学年份">{{ data.enroll_year }}</el-descriptions-item>
          <el-descriptions-item label="归档">{{ data.is_final==='1'?'已归档':'在校' }}</el-descriptions-item>
        </el-descriptions>
        <el-divider>档案信息</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="家庭信息">
            <div v-if="familyList.length">
              <div v-for="(m,i) in familyList" :key="i">家庭成员：{{ m.member || '-' }}，关系：{{ m.relation || '-' }}</div>
            </div>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="健康信息">{{ data.health_info || '-' }}</el-descriptions-item>
          <el-descriptions-item label="奖惩">{{ data.award_punish || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ data.remark || '-' }}</el-descriptions-item>
          <el-descriptions-item label="紧急联系人">{{ data.emergency_contact || '-' }}</el-descriptions-item>
          <el-descriptions-item label="紧急电话">{{ data.emergency_phone || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { useAuthStore } from '@/stores/auth'
const auth=useAuthStore()
const loading=ref(false)
const data=ref<any>({})
const familyList=computed(()=>{
  const raw=data.value.family_info
  if(!raw) return []
  try{
    const arr=JSON.parse(raw)
    if(Array.isArray(arr)) return arr.filter((x:any)=> x.member||x.relation)
  }catch{}
  return raw? [{member: raw, relation:''}] : []
})
async function load(){
  loading.value=true
  try{
    const sid=auth.studentId || localStorage.getItem('studentId')
    if(!sid) return
    const res:any=await request.get(`/student/queryById/${sid}`)
    data.value=res?.data ?? {}
    // 同步姓名到全局
    if(data.value.name && data.value.name!==auth.name){
      auth.name=data.value.name
      localStorage.setItem('studentName', data.value.name)
    }
  }finally{ loading.value=false }
}
onMounted(load)
</script>
