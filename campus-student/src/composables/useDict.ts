import { ref, onMounted } from 'vue'
import request from '@/utils/request'

export function useDict(type: string) {
  const dict = ref<any[]>([])
  onMounted(async () => {
    try {
      const res: any = await request.get(`/dictData/type/${type}`)
      dict.value = res?.data || []
    } catch {
      dict.value = []
    }
  })
  return dict
}
