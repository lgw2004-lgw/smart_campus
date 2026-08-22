import { createRouter, createWebHistory } from 'vue-router'
const router=createRouter({
  history:createWebHistory(),
  routes:[
    {path:'/login', component:()=>import('@/views/Login.vue')},
    {path:'/', component:()=>import('@/views/Layout.vue'), redirect:'/home', children:[
      {path:'home', component:()=>import('@/views/Home.vue'), meta:{title:'首页'}},
      {path:'courses', component:()=>import('@/views/Courses.vue'), meta:{title:'选课大厅'}},
      {path:'my-enroll', component:()=>import('@/views/MyEnroll.vue'), meta:{title:'我的选课'}},
      {path:'my-fee', component:()=>import('@/views/MyFee.vue'), meta:{title:'我的缴费'}},
      {path:'my-dorm', component:()=>import('@/views/MyDorm.vue'), meta:{title:'我的宿舍'}},
      {path:'my-book', component:()=>import('@/views/MyBook.vue'), meta:{title:'图书借阅'}},
      {path:'my-score', component:()=>import('@/views/MyScore.vue'), meta:{title:'我的成绩'}},
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
