import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: {
    proxy: {
      '/userAuth': 'http://127.0.0.1:18367',
      '/memberAuth': 'http://127.0.0.1:18367',
      '/user': 'http://127.0.0.1:18367',
      '/role': 'http://127.0.0.1:18367',
      '/menu': 'http://127.0.0.1:18367',
      '/dept': 'http://127.0.0.1:18367',
      '/dict': 'http://127.0.0.1:18367',
      '/dictData': 'http://127.0.0.1:18367',
      '/dictType': 'http://127.0.0.1:18367',
      '/notice': 'http://127.0.0.1:18367',
      '/news': 'http://127.0.0.1:18367',
      '/banner': 'http://127.0.0.1:18367',
      '/loginInfo': 'http://127.0.0.1:18367',
      '/operLog': 'http://127.0.0.1:18367',
      '/student': 'http://127.0.0.1:18367',
      '/studentFile': 'http://127.0.0.1:18367',
      '/course': 'http://127.0.0.1:18367',
      '/scheduling': 'http://127.0.0.1:18367',
      '/enrollment': 'http://127.0.0.1:18367',
      '/exam': 'http://127.0.0.1:18367',
      '/examPaper': 'http://127.0.0.1:18367',
      '/score': 'http://127.0.0.1:18367',
      '/class': 'http://127.0.0.1:18367',
      '/dorm': 'http://127.0.0.1:18367',
      '/building': 'http://127.0.0.1:18367',
      '/room': 'http://127.0.0.1:18367',
      '/media': 'http://127.0.0.1:18367',
      '/book': 'http://127.0.0.1:18367',
      '/borrow': 'http://127.0.0.1:18367',
      '/fee': 'http://127.0.0.1:18367',
      '/weChatPay': 'http://127.0.0.1:18367',
      '/feeOrder': 'http://127.0.0.1:18367'
    }
  }
})
