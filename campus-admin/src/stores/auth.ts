import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userName = ref(localStorage.getItem('userName') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const workNo = ref(localStorage.getItem('workNo') || '')
  const userType = ref(localStorage.getItem('userType') || '')
  const deptId = ref(localStorage.getItem('deptId') || '')

  async function login(userNameVal: string, password: string, isStudent = false) {
    const url = isStudent ? '/memberAuth/login' : '/userAuth/login'
    const res: any = await request.get(url, { params: { workNo: userNameVal, userName: userNameVal, password } })
    const data = res.data
    token.value = data.token
    userName.value = data.userName
    userId.value = String(data.userId)
    workNo.value = data.workNo || ''
    userType.value = String(data.userType || '')
    deptId.value = data.deptId ? String(data.deptId) : ''
    localStorage.setItem('token', data.token)
    localStorage.setItem('userName', data.userName)
    localStorage.setItem('userId', String(data.userId))
    localStorage.setItem('workNo', data.workNo || '')
    localStorage.setItem('userType', String(data.userType || ''))
    localStorage.setItem('deptId', data.deptId ? String(data.deptId) : '')
    return data
  }

  function logout() {
    token.value = ''
    userName.value = ''
    userId.value = ''
    workNo.value = ''
    userType.value = ''
    deptId.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    localStorage.removeItem('userId')
    localStorage.removeItem('workNo')
    localStorage.removeItem('userType')
    localStorage.removeItem('deptId')
  }

  return { token, userName, userId, workNo, userType, deptId, login, logout }
})
