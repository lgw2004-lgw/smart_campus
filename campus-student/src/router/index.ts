import { createRouter, createWebHashHistory } from 'vue-router'
const router=createRouter({
  history:createWebHashHistory(),
  routes:[
    {path:'/login', component:()=>import('@/views/Login.vue')},
    {path:'/', component:()=>import('@/views/Layout.vue'), redirect:'/home', children:[
      {path:'home', component:()=>import('@/views/Home.vue'), meta:{title:'首页'}},
      {path:'courses', component:()=>import('@/views/Courses.vue'), meta:{title:'选课大厅'}},
      {path:'my-enroll', component:()=>import('@/views/MyEnroll.vue'), meta:{title:'我的选课'}},
      {path:'timetable', component:()=>import('@/views/Timetable.vue'), meta:{title:'我的课表'}},
      {path:'my-exam', component:()=>import('@/views/MyExam.vue'), meta:{title:'考试信息'}},
      {path:'my-attendance', component:()=>import('@/views/MyAttendance.vue'), meta:{title:'考勤签到'}},
      {path:'retake-signup', component:()=>import('@/views/RetakeSignup.vue'), meta:{title:'补考报名'}},
      {path:'my-evaluation', component:()=>import('@/views/MyEvaluation.vue'), meta:{title:'课程评教'}},
      {path:'my-leave', component:()=>import('@/views/MyLeave.vue'), meta:{title:'请假申请'}},
      {path:'my-message', component:()=>import('@/views/MyMessage.vue'), meta:{title:'消息中心'}},
      {path:'plan', component:()=>import('@/views/Plan.vue'), meta:{title:'个人培养方案'}},
      {path:'my-fee', component:()=>import('@/views/MyFee.vue'), meta:{title:'我的缴费'}},
      {path:'my-dorm', component:()=>import('@/views/MyDorm.vue'), meta:{title:'我的宿舍'}},
      {path:'my-book', component:()=>import('@/views/MyBook.vue'), meta:{title:'图书借阅'}},
      {path:'book-store', component:()=>import('@/views/BookStore.vue'), meta:{title:'书库'}},
      {path:'my-borrow', component:()=>import('@/views/MyBorrow.vue'), meta:{title:'我的借阅'}},
      {path:'my-score', component:()=>import('@/views/MyScore.vue'), meta:{title:'我的成绩'}},
      {path:'profile', component:()=>import('@/views/Profile.vue'), meta:{title:'个人资料'}},
      {path:'notices', component:()=>import('@/views/Notices.vue'), meta:{title:'公告资讯'}},
    ]}
  ]
})
router.beforeEach((to,_f,next)=>{
  const t=localStorage.getItem('student_token')
  if(to.path!=='/login' && !t) return next('/login')
  next()
})
export default router
