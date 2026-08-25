import request from '@/utils/request'

export async function downloadFile(url: string, params: Record<string, any> = {}, filename = '导出.xlsx') {
  const res: any = await request.get(url, { params, responseType: 'blob' })
  const blob = res instanceof Blob ? res : new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}
