import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/login', component: () => import('@/views/Login.vue') },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      redirect: '/home',
      children: [
        { path: 'home', component: () => import('@/views/home/Dashboard.vue'), meta: { title: '首页看板' } },
        // academic
        { path: 'academic/course', component: () => import('@/views/academic/Course.vue'), meta: { title: '课程管理' } },
        { path: 'academic/scheduling', component: () => import('@/views/academic/Scheduling.vue'), meta: { title: '排课管理' } },
        { path: 'academic/enrollment', component: () => import('@/views/academic/Enrollment.vue'), meta: { title: '选课管理' } },
        { path: 'academic/score', component: () => import('@/views/academic/Score.vue'), meta: { title: '成绩管理' } },
        // student
        { path: 'student/list', component: () => import('@/views/student/List.vue'), meta: { title: '学生档案' } },
        { path: 'student/class', component: () => import('@/views/student/Class.vue'), meta: { title: '班级管理' } },
        // resource
        { path: 'resource/dorm', component: () => import('@/views/resource/Dorm.vue'), meta: { title: '宿舍管理' } },
        { path: 'resource/book', component: () => import('@/views/resource/Book.vue'), meta: { title: '图书管理' } },
        // finance
        { path: 'finance/fee', component: () => import('@/views/finance/Fee.vue'), meta: { title: '缴费管理' } },
        // content
        { path: 'content/notice', component: () => import('@/views/content/Notice.vue'), meta: { title: '公告管理' } },
        { path: 'content/banner', component: () => import('@/views/content/Banner.vue'), meta: { title: '轮播管理' } },
        // system
        { path: 'system/user', component: () => import('@/views/system/User.vue'), meta: { title: '用户管理' } },
        { path: 'system/role', component: () => import('@/views/system/Role.vue'), meta: { title: '角色管理' } },
        { path: 'system/menu', component: () => import('@/views/system/Menu.vue'), meta: { title: '菜单管理' } },
        { path: 'system/dept', component: () => import('@/views/system/Dept.vue'), meta: { title: '院系管理' } },
        { path: 'system/dict', component: () => import('@/views/system/Dict.vue'), meta: { title: '字典管理' } },
        { path: 'system/log', component: () => import('@/views/system/Log.vue'), meta: { title: '日志管理' } },
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) return next('/login')
  next()
})

export default router
