import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
export default defineConfig({
  plugins:[vue()],
  resolve:{ alias:{'@':path.resolve(__dirname,'src')} },
  server:{
    port:5174,
    proxy:{
      '/memberAuth':'http://127.0.0.1:18367',
      '/userAuth':'http://127.0.0.1:18367',
      '/student':'http://127.0.0.1:18367',
      '/studentFile':'http://127.0.0.1:18367',
      '/course':'http://127.0.0.1:18367',
      '/scheduling':'http://127.0.0.1:18367',
      '/enrollment':'http://127.0.0.1:18367',
      '/fee':'http://127.0.0.1:18367',
      '/weChatPay':'http://127.0.0.1:18367',
      '/feeOrder':'http://127.0.0.1:18367',
      '/dorm':'http://127.0.0.1:18367',
      '/book':'http://127.0.0.1:18367',
      '/borrow':'http://127.0.0.1:18367',
      '/score':'http://127.0.0.1:18367',
      '/notice':'http://127.0.0.1:18367',
      '/banner':'http://127.0.0.1:18367',
      '/dictData':'http://127.0.0.1:18367'
    }
  }
})
