import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useDictStore = defineStore('dict', {
  state: () => ({ cache: {} as Record<string, any[]> }),
  actions: {
    async getDict(type: string) {
      if (this.cache[type]) return this.cache[type]
      const res: any = await request.get(`/dictData/type/${type}`)
      this.cache[type] = res.data || []
      return this.cache[type]
    }
  }
})
