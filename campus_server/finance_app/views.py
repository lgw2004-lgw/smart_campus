from utils.base_view import BaseView
from utils.response import success, error, page_response
from utils.pagination import get_page_params
from utils.gen_id import gen_id
from .models import FeeOrder, FeeOrderItem, FeeRefund, FeeTuitionConfig
from academic_app.models import AcaEnrollment, AcaCourse, AcaScore
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
        if order.order_status == '3':
            return success({"orderId": order.order_id, "orderStatus": "3"})
        order.order_status = '3'
        order.pay_time = datetime.datetime.now()
        order.save(update_fields=['order_status','pay_time'])
        # 同步选课状态 0->1 仅对 NORMAL/RETAKE 关联选课
        if order.order_type in ('NORMAL','RETAKE') and order.ch_id:
            enroll_ids = [x for x in order.ch_id.split(',') if x]
            if enroll_ids:
                AcaEnrollment.objects.filter(enroll_id__in=enroll_ids, status='0').update(status='1')
        # TUITION 无需同步选课，缴费即具备选课资格
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
            # 仅 NORMAL/RETAKE 关联选课
            if order.order_type in ('NORMAL','RETAKE'):
                AcaEnrollment.objects.filter(enroll_id__in=[x for x in order.ch_id.split(',') if x], status='1').update(status='2')
        return success({"refundId": refund_id, "refundAmount": refund_amount})

# ---- 总学费（新） ----
class TuitionSaveView(BaseView):
    """POST /fee/tuition/save {semester,totalAmount,detail} 管理员发布"""
    def post(self, request):
        body = self.parse_body(request)
        semester = body.get('semester') or body.get('Semester')
        total = body.get('totalAmount') or body.get('total_amount') or body.get('amount')
        detail = body.get('detail') or ''
        if not semester or total is None:
            return error("semester与totalAmount必填", code=400)
        try:
            total_f = float(total)
        except:
            return error("totalAmount 非法", code=400)
        obj, created = FeeTuitionConfig.objects.update_or_create(semester=semester, defaults={'total_amount': total_f, 'detail': detail})
        return success({"semester": semester, "totalAmount": float(obj.total_amount), "created": created})

class TuitionQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = FeeTuitionConfig.objects.all()
        if data.get('semester'): qs = qs.filter(semester__icontains=data['semester'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class TuitionGetView(BaseView):
    def get(self, request):
        semester = request.GET.get('semester') or request.GET.get('Semester')
        if semester:
            try:
                obj = FeeTuitionConfig.objects.get(semester=semester)
                return success({"semester": obj.semester, "totalAmount": float(obj.total_amount), "detail": obj.detail})
            except FeeTuitionConfig.DoesNotExist:
                return error("该学期未发布学费", code=404)
        # 未传则返回最新一条
        obj = FeeTuitionConfig.objects.order_by('-create_time').first()
        if not obj:
            return error("尚未发布任何学费", code=404)
        return success({"semester": obj.semester, "totalAmount": float(obj.total_amount), "detail": obj.detail})

class TuitionPayView(BaseView):
    """POST /fee/tuition/pay {studentId,semester} 一次性总学费"""
    def post(self, request):
        body = self.parse_body(request)
        student_id = body.get('studentId') or body.get('student_id')
        semester = body.get('semester')
        if not student_id:
            return error("studentId必填", code=400)
        # 若未传semester取最新
        if not semester:
            cfg = FeeTuitionConfig.objects.order_by('-create_time').first()
            if not cfg:
                return error("尚未发布学费", code=400)
            semester = cfg.semester
            total = float(cfg.total_amount)
            detail = cfg.detail
        else:
            try:
                cfg = FeeTuitionConfig.objects.get(semester=semester)
                total = float(cfg.total_amount); detail = cfg.detail
            except FeeTuitionConfig.DoesNotExist:
                return error("该学期学费未发布", code=404)
        # 幂等：已缴则不重复
        if FeeOrder.objects.filter(student_id=student_id, semester=semester, order_type='TUITION', order_status='3').exists():
            return error("该学期总学费已缴", code=400)
        # 若有待付则返回已有
        existing = FeeOrder.objects.filter(student_id=student_id, semester=semester, order_type='TUITION', order_status='0').first()
        if existing:
            return success({"orderId": existing.order_id, "orderAmount": float(existing.order_amount), "semester": semester})
        order_id = gen_id('ORD')
        FeeOrder.objects.create(order_id=order_id, student_id=student_id, order_amount=total, order_status='0', order_type='TUITION', semester=semester, detail=detail, ch_id='')
        return success({"orderId": order_id, "orderAmount": total, "semester": semester})

class RetakeFeeCalcView(BaseView):
    """POST /fee/retake/calc {studentId,courseId} 按学分*100"""
    def post(self, request):
        body = self.parse_body(request)
        course_id = body.get('courseId') or body.get('course_id')
        if not course_id:
            return error("courseId必填", code=400)
        try:
            crs = AcaCourse.objects.get(course_id=course_id)
            price = float(crs.credit or 3)*100
        except AcaCourse.DoesNotExist:
            return error("课程不存在", code=404)
        return success({"courseId": course_id, "retakeFee": price, "credit": float(crs.credit or 3)})

class RetakeEnrollView(BaseView):
    """POST /fee/retake/enroll 缩合：选重修课并自动计重修费（若已缴总学费则仅收重修费）"""
    def post(self, request):
        body = self.parse_body(request)
        student_id = body.get('studentId') or body.get('student_id')
        course_id = body.get('courseId') or body.get('course_id')
        semester = body.get('semester')
        if not student_id or not course_id:
            return error("studentId与courseId必填", code=400)
        # 复用选课校验（需已缴总学费）
        from academic_app.models import StuStudent
        try:
            stu = StuStudent.objects.get(student_id=student_id)
            if stu.is_final=='1':
                return error("已归档", code=400)
        except StuStudent.DoesNotExist:
            return error("学生不存在", code=404)
        # 总学费校验
        sem = semester or (FeeTuitionConfig.objects.order_by('-create_time').first().semester if FeeTuitionConfig.objects.exists() else None)
        if sem and not FeeOrder.objects.filter(student_id=student_id, semester=sem, order_type='TUITION', order_status='3').exists():
            return error("请先缴纳总学费", code=400)
        if AcaEnrollment.objects.filter(student_id=student_id, course_id=course_id, status__in=['0','1']).exists():
            return error("已选该课程", code=400)
        # 判断是否重修（已有成绩）
        is_retake = AcaScore.objects.filter(student_id=student_id, course_id=course_id).exists()
        if not is_retake:
            return error("该课程非重修（无历史成绩），请走正常选课", code=400)
        # 创建选课
        enroll_id = gen_id('ENR')
        AcaEnrollment.objects.create(enroll_id=enroll_id, student_id=student_id, course_id=course_id, status='0')
        # 计重修费
        try:
            crs = AcaCourse.objects.get(course_id=course_id)
            price = float(crs.credit or 3)*100
        except:
            price = 300
        order_id = gen_id('ORD')
        # 取学期
        if not semester:
            semester = sem or '2024-2025-1'
        FeeOrder.objects.create(order_id=order_id, student_id=student_id, order_amount=price, order_status='0', order_type='RETAKE', semester=semester, ch_id=enroll_id, detail=f"重修 {course_id}")
        FeeOrderItem.objects.create(item_id=gen_id('ITEM'), order_id=order_id, ref_id=enroll_id, item_name=crs.course_name if 'crs' in locals() else course_id, item_price=price, item_num=1, item_amount=price)
        return success({"enrollId": enroll_id, "orderId": order_id, "retakeFee": price})


# ================= 一卡通账户 =================
from .models import FinCardAccount, FinCardTransaction
from django.utils import timezone as _tz

def _ensure_card(student_id):
    acc = FinCardAccount.objects.filter(student_id=student_id).first()
    if not acc:
        acc = FinCardAccount.objects.create(student_id=student_id, balance=0)
    return acc

class CardAccountView(BaseView):
    def get(self, request):
        student_id = request.GET.get('studentId')
        if not student_id:
            return error("studentId 必填", code=400)
        acc = _ensure_card(student_id)
        return success({"studentId": student_id, "balance": float(acc.balance)})

class CardRechargeView(BaseView):
    def post(self, request):
        import decimal
        body = self.parse_body(request)
        student_id = body.get('studentId'); amount = body.get('amount')
        try:
            amount = decimal.Decimal(str(amount))
        except:
            return error("amount 非法", code=400)
        if amount <= 0 or amount > 10000:
            return error("充值金额须在 0.01-10000 之间", code=400)
        acc = _ensure_card(student_id)
        acc.balance = decimal.Decimal(acc.balance) + amount
        acc.update_time = _tz.now(); acc.save(update_fields=['balance','update_time'])
        tx = FinCardTransaction.objects.create(tx_id=gen_id('TX'), student_id=student_id, tx_type='1',
            amount=amount, balance_after=acc.balance, scene='充值')
        return success({"txId": tx.tx_id, "balance": float(acc.balance)})

class CardConsumeView(BaseView):
    def post(self, request):
        import decimal
        body = self.parse_body(request)
        student_id = body.get('studentId'); amount = body.get('amount'); scene = body.get('scene') or '食堂'
        try:
            amount = decimal.Decimal(str(amount))
        except:
            return error("amount 非法", code=400)
        if amount <= 0:
            return error("消费金额须大于0", code=400)
        acc = _ensure_card(student_id)
        if decimal.Decimal(acc.balance) < amount:
            return error("余额不足，请先充值", code=400)
        acc.balance = decimal.Decimal(acc.balance) - amount
        acc.update_time = _tz.now(); acc.save(update_fields=['balance','update_time'])
        tx = FinCardTransaction.objects.create(tx_id=gen_id('TX'), student_id=student_id, tx_type='2',
            amount=amount, balance_after=acc.balance, scene=scene, ref_id=body.get('refId'))
        return success({"txId": tx.tx_id, "balance": float(acc.balance)})

class CardTxQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = FinCardTransaction.objects.all().order_by('-tx_id')
        if data.get('studentId'):
            qs = qs.filter(student_id=data['studentId'])
        if data.get('txType'):
            qs = qs.filter(tx_type=data['txType'])
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class CardAccountsAdminView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = FinCardAccount.objects.all().order_by('-update_time')
        if data.get('studentId'):
            qs = qs.filter(student_id__icontains=data['studentId'])
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)


class FeeOrderExportView(BaseView):
    """缴费清单导出：GET /feeOrder/export?orderStatus=&orderType="""
    def get(self, request):
        qs = FeeOrder.objects.all().order_by('-create_time')
        st = request.GET.get('orderStatus'); ot = request.GET.get('orderType'); sid = request.GET.get('studentId')
        if st: qs = qs.filter(order_status=st)
        if ot: qs = qs.filter(order_type=ot)
        if sid: qs = qs.filter(student_id=sid)
        rows = []
        for o in qs[:5000]:
            rows.append({'订单号': o.order_id, '学号': o.student_id, '金额': float(o.order_amount or 0),
                '状态': {'0':'未支付','3':'已支付','2':'已关闭'}.get(o.order_status, o.order_status),
                '类型': {'TUITION':'学费','RETAKE':'重修/补考','NORMAL':'普通'}.get(o.order_type, o.order_type),
                '学期': o.semester, '说明': o.detail, '创建时间': str(o.create_time)[:19]})
        return _xlsx_response(rows, ['订单号','学号','金额','状态','类型','学期','说明','创建时间'], '缴费清单')


def _xlsx_response(rows, headers, filename):
    from openpyxl import Workbook
    from io import BytesIO
    from django.http import HttpResponse
    from urllib.parse import quote
    wb = Workbook(); ws = wb.active; ws.title = 'sheet1'
    ws.append(headers)
    for r in rows: ws.append([r.get(h) if isinstance(r, dict) else r for h in headers])
    buf = BytesIO(); wb.save(buf)
    resp = HttpResponse(buf.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f"attachment; filename*=UTF-8''{quote(filename)}.xlsx"
    return resp
