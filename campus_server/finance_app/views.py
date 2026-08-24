from utils.base_view import BaseView
from utils.response import success, error, page_response
from utils.pagination import get_page_params
from utils.gen_id import gen_id
from .models import FeeOrder, FeeOrderItem, FeeRefund
from academic_app.models import AcaEnrollment, AcaCourse
import datetime
import qrcode
import base64
from io import BytesIO

class FeeCalcView(BaseView):
    """POST /fee/calc {enrollIds} -> 计费（按学分*100 演示）"""
    def post(self, request):
        body = self.parse_body(request)
        enroll_ids = body.get('enrollIds') or body.get('enroll_ids') or []
        if not enroll_ids:
            return error("enrollIds 不能为空", code=400)
        enrolls = list(AcaEnrollment.objects.filter(enroll_id__in=enroll_ids).values())
        total = 0
        items = []
        for en in enrolls:
            try:
                course = AcaCourse.objects.get(course_id=en['course_id'])
                price = float(course.credit or 3) * 100  # 每学分100元
                name = course.course_name
            except Exception:
                price = 300
                name = en['course_id']
            items.append({"enrollId": en['enroll_id'], "courseId": en['course_id'], "itemName": name, "itemPrice": price})
            total += price
        return success({"totalAmount": total, "items": items})

class FeePayMsgView(BaseView):
    """POST /fee/payMsg {studentId, enrollIds}"""
    def post(self, request):
        body = self.parse_body(request)
        student_id = body.get('studentId') or body.get('student_id')
        enroll_ids = body.get('enrollIds') or body.get('enroll_ids') or []
        if not student_id or not enroll_ids:
            return error("studentId/enrollIds 不能为空", code=400)
        # 复用计费逻辑
        total = 0
        items_data = []
        for eid in enroll_ids:
            try:
                en = AcaEnrollment.objects.get(enroll_id=eid)
                course = AcaCourse.objects.get(course_id=en.course_id)
                price = float(course.credit or 3) * 100
                items_data.append((en, course, price))
                total += price
            except Exception:
                items_data.append((None, None, 300))
                total += 300
        order_id = gen_id('ORD')
        order = FeeOrder.objects.create(order_id=order_id, student_id=student_id, order_amount=total, order_status='0', ch_id=','.join(enroll_ids))
        for en, course, price in items_data:
            item_id = gen_id('ITEM')
            FeeOrderItem.objects.create(item_id=item_id, order_id=order_id, ref_id=en.enroll_id if en else '', item_name=course.course_name if course else '', item_price=price, item_num=1, item_amount=price)
        return success({"orderId": order_id, "orderNo": order_id, "orderAmount": total})

class WeChatNativeCodeView(BaseView):
    """POST /weChatPay/getNativeCodeUrl/{orderId} -> 返回二维码 base64"""
    def post(self, request, order_id):
        try:
            order = FeeOrder.objects.get(order_id=order_id)
        except FeeOrder.DoesNotExist:
            return error("订单不存在", code=404)
        # 模拟微信 Native URL
        pay_url = f"weixin://wxpay/bizpayurl?pr={order_id}"
        # 生成二维码
        img = qrcode.make(pay_url)
        buf = BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return success({"codeUrl": pay_url, "qrCode": f"data:image/png;base64,{b64}", "orderId": order_id})

class WeChatPayStatusView(BaseView):
    """GET /weChatPay/getPayStatus/{orderNo} 模拟轮询，一次即摘要成功"""
    def get(self, request, order_no):
        try:
            order = FeeOrder.objects.get(order_id=order_no)
        except FeeOrder.DoesNotExist:
            return error("订单不存在", code=404)
        # 模拟：查询即视为可支付，返回状态
        return success({"orderId": order.order_id, "orderNo": order.order_id, "orderStatus": order.order_status, "orderAmount": float(order.order_amount)})

class FeeOrderUpdateView(BaseView):
    """POST /feeOrder/updateById/{orderNo}"""
    def post(self, request, order_no):
        try:
            order = FeeOrder.objects.get(order_id=order_no)
        except FeeOrder.DoesNotExist:
            return error("订单不存在", code=404)
        order.order_status = '3'
        order.pay_time = datetime.datetime.now()
        order.save(update_fields=['order_status','pay_time'])
        # 同步选课状态 0->1
        if order.ch_id:
            enroll_ids = order.ch_id.split(',')
            AcaEnrollment.objects.filter(enroll_id__in=enroll_ids, status='0').update(status='1')
        return success({"orderId": order.order_id, "orderStatus": "3"})

class FeeOrderQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = FeeOrder.objects.all()
        if data.get('studentId'):
            qs = qs.filter(student_id=data['studentId'])
        if data.get('orderStatus'):
            qs = qs.filter(order_status=data['orderStatus'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class FeeRefundView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        order_id = body.get('orderId') or body.get('order_id')
        try:
            order = FeeOrder.objects.get(order_id=order_id)
        except FeeOrder.DoesNotExist:
            return error("订单不存在", code=404)
        if order.order_status != '3':
            return error("仅已付订单可退费", code=400)
        if FeeRefund.objects.filter(order_id=order_id).exists():
            return error("该订单已退费", code=400)
        # 退费金额：若前端未传则按“总费 - 单次课费(按学分*100/考勤)”计算
        req_amount = body.get('refundAmount') or body.get('refund_amount')
        if req_amount is not None and str(req_amount) != '':
            try:
                refund_amount = float(req_amount)
            except:
                return error("refundAmount 非法", code=400)
        else:
            # 自动计算：总费 - 单门课费（首门课 credit*100）
            try:
                first_enroll_id = (order.ch_id or '').split(',')[0]
                en = AcaEnrollment.objects.get(enroll_id=first_enroll_id)
                crs = AcaCourse.objects.get(course_id=en.course_id)
                single_fee = float(crs.credit or 3) * 100
            except Exception:
                single_fee = 300
            # 若已上课，扣除单次课费（50/次），未上课全退
            from academic_app.models import AcaAttendance
            attended = AcaAttendance.objects.filter(student_id=order.student_id).count()
            deduction = 50 * attended
            refund_amount = float(order.order_amount) - deduction
            if refund_amount < 0: refund_amount = 0
            # 单课全退兼容：若 deduction==0 则全额
            if attended==0:
                refund_amount = float(order.order_amount)
        if refund_amount > float(order.order_amount):
            return error("退费金额不能超过订单金额", code=400)
        refund_id = gen_id('RFD')
        FeeRefund.objects.create(refund_id=refund_id, order_id=order_id, refund_amount=refund_amount, refund_status='1', reason=body.get('reason') or body.get('refundReason'))
        # 退选关联选课 + 考试资格置false（status 1→2 后 ScoreAddView 将拦截）
        if order.ch_id:
            AcaEnrollment.objects.filter(enroll_id__in=order.ch_id.split(','), status='1').update(status='2')
        return success({"refundId": refund_id, "refundAmount": refund_amount})
