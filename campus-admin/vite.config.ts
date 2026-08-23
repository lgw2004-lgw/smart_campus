import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

const proxyTarget = 'http://127.0.0.1:18367'
const apiPrefixes = ['/userAuth','/memberAuth','/user','/role','/menu','/dept','/dict','/dictData','/dictType','/notice','/news','/banner','/loginInfo','/operLog','/student','/studentFile','/course','/scheduling','/enrollment','/exam','/examPaper','/score','/class','/dorm','/building','/room','/media','/book','/borrow','/fee','/weChatPay','/feeOrder']
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
  plugins: [vue()],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: { proxy }
})
