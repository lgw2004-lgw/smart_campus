import request from '@/utils/request'
// 通用分页
export const postPage = (url:string, data:any) => request.post(url, data)
// 字典
export const getDict = (type:string) => request.get(`/dictData/type/${type}`)
// 课程
export const querySelectable = (studentId:string, semester?:string) => request.get('/course/querySelectable', {params:{studentId, semester}})
// 缴费
export const feeCalc = (enrollIds:string[]) => request.post('/fee/calc', {enrollIds})
export const feePayMsg = (studentId:string, enrollIds:string[]) => request.post('/fee/payMsg', {studentId, enrollIds})
export const getNativeCode = (orderId:string) => request.post(`/weChatPay/getNativeCodeUrl/${orderId}`)
export const getPayStatus = (orderNo:string) => request.get(`/weChatPay/getPayStatus/${orderNo}`)
export const payConfirm = (orderNo:string) => request.post(`/feeOrder/updateById/${orderNo}`)
