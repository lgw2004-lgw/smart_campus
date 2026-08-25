import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
const proxyTarget = 'http://127.0.0.1:18367'
const apiPrefixes = ['/memberAuth','/userAuth','/user','/dept','/dict','/dictData','/student','/studentFile','/course','/scheduling','/enrollment','/fee','/weChatPay','/feeOrder','/dorm','/building','/book','/borrow','/score','/notice','/banner','/plan','/classroom','/attendance','/exam','/examPaper','/class','/warning','/evaluation','/leave','/message','/card']
const proxy: Record<string, any> = {}
for (const p of apiPrefixes) {
  proxy[p] = {
    target: proxyTarget,
    changeOrigin: true,
    bypass: (req: any) => {
      if (req.headers.accept?.includes('text/html')) return '/index.html'
    }
  }
}
export default defineConfig({
  plugins:[vue()],
  resolve:{ alias:{'@':path.resolve(__dirname,'src')} },
  server:{
    port:5174,
    proxy
  }
})
