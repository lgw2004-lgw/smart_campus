import axios from 'axios'
import { ElMessage } from 'element-plus'
const request=axios.create({timeout:10000})
request.interceptors.request.use(c=>{ const t=localStorage.getItem('student_token'); if(t) (c.headers as any)['token']=t; return c })
request.interceptors.response.use(res=>{
  const d=res.data
  if(d && typeof d.code!=='undefined' && d.code!==200){ ElMessage.error(d.message||'请求失败'); return Promise.reject(d) }
  return d
}, e=>{ ElMessage.error(e.message||'网络错误'); return Promise.reject(e) })
export default request
