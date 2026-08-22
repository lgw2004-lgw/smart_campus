import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'
export const useAuthStore=defineStore('studentAuth',()=>{
  const token=ref(localStorage.getItem('student_token')||'')
  const studentId=ref(localStorage.getItem('studentId')||'')
  const name=ref(localStorage.getItem('studentName')||'')
  async function login(id:string, pwd:string){
    const res:any=await request.get('/memberAuth/login', {params:{userName:id,password:pwd}})
    token.value=res.data.token; studentId.value=res.data.userId; name.value=res.data.userName
    localStorage.setItem('student_token',res.data.token)
    localStorage.setItem('studentId',res.data.userId)
    localStorage.setItem('studentName',res.data.userName)
    return res.data
  }
  function logout(){ token.value=''; localStorage.removeItem('student_token'); localStorage.removeItem('studentId'); localStorage.removeItem('studentName') }
  return {token, studentId, name, login, logout}
})
