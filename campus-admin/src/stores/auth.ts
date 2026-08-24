import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userName = ref(localStorage.getItem('userName') || '')
  const userId = ref(localStorage.getItem('userId') || '')

  async function login(userNameVal: string, password: string, isStudent = false) {
    const url = isStudent ? '/memberAuth/login' : '/userAuth/login'
    const res: any = await request.get(url, { params: { workNo: userNameVal, userName: userNameVal, password } })
    const data = res.data
    token.value = data.token
    userName.value = data.userName
    userId.value = String(data.userId)
    localStorage.setItem('token', data.token)
    localStorage.setItem('userName', data.userName)
    localStorage.setItem('userId', String(data.userId))
    return data
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    localStorage.removeItem('userId')
  }

  return { token, userName, userId, login, logout }
})
