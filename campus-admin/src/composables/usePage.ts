import { ref, reactive } from 'vue'
import request from '@/utils/request'

export function usePage(url: string, defaultQuery: any = {}) {
  const loading = ref(false)
  const total = ref(0)
  const pageNo = ref(1)
  const pageSize = ref(10)
  const query = reactive({ ...defaultQuery })
  const list = ref<any[]>([])

  async function fetch() {
    loading.value = true
    try {
      const res: any = await request.post(url, { pageNo: pageNo.value, pageSize: pageSize.value, data: query })
      const data = res.data
      list.value = data.list || []
      total.value = data.total || 0
    } finally {
      loading.value = false
    }
  }

  function handleCurrentChange(val: number) {
    pageNo.value = val
    fetch()
  }

  function handleSizeChange(val: number) {
    pageSize.value = val
    fetch()
  }

  function search() {
    pageNo.value = 1
    fetch()
  }

  return { loading, total, pageNo, pageSize, query, list, fetch, handleCurrentChange, handleSizeChange, search }
}
