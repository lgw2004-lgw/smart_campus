import { onMounted, ref } from 'vue'
import { useDictStore } from '@/stores/dict'

export function useDict(type: string) {
  const dict = ref<any[]>([])
  const store = useDictStore()
  onMounted(async () => {
    dict.value = await store.getDict(type)
  })
  return dict
}
