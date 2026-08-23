from utils.base_view import BaseView
from utils.response import success, error, page_response
from utils.pagination import get_page_params
from utils.gen_id import gen_id
from .models import StuStudent, StuStudentFile, StuClass, AcaCourse, AcaScheduling, AcaEnrollment, AcaExam, AcaScore
import json

# ---- 学生建档 ----
class StudentQueryByIdCardView(BaseView):
    def get(self, request):
        id_card = request.GET.get('idCard') or request.GET.get('id_card')
        if not id_card:
            return error("idCard 不能为空", code=400)
        try:
            stu = StuStudent.objects.get(id_card=id_card)
            return success({k: getattr(stu, k) for k in ['student_id','name','sex','id_card','phone','dept_id','class_id','enroll_year','avatar']})
        except StuStudent.DoesNotExist:
            return error("未找到学生", code=404)

class StudentAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        sid = body.get('studentId') or gen_id('STU')
        if StuStudent.objects.filter(student_id=sid).exists():
            return error("学号已存在", code=400)
        if body.get('idCard') and StuStudent.objects.filter(id_card=body['idCard']).exists():
            return error("身份证已存在", code=400)
        stu = StuStudent.objects.create(
            student_id=sid,
            name=body.get('name') or body.get('studentName'),
            sex=body.get('sex','0'),
            id_card=body.get('idCard'),
            phone=body.get('phone'),
            dept_id=body.get('deptId'),
            class_id=body.get('classId'),
            enroll_year=body.get('enrollYear'),
            avatar=body.get('avatar'),
        )
        return success({"studentId": stu.student_id})

class StudentQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = StuStudent.objects.all()
        if data.get('name'):
            qs = qs.filter(name__icontains=data['name'])
        if data.get('deptId'):
            qs = qs.filter(dept_id=data['deptId'])
        if data.get('classId'):
            qs = qs.filter(class_id=data['classId'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class StudentFileAddView(BaseView):
    def put(self, request):
        body = self.parse_body(request)
        sid = body.get('studentId') or body.get('student_id')
        if not sid:
            return error("studentId 不能为空", code=400)
        defaults = {
            'family_info': body.get('familyInfo') or body.get('family_info'),
            'health_info': body.get('healthInfo') or body.get('health_info'),
            'award_punish': body.get('awardPunish') or body.get('award_punish'),
            'remark': body.get('remark'),
            'emergency_contact': body.get('emergencyContact') or body.get('emergency_contact'),
        }
        obj, created = StuStudentFile.objects.update_or_create(student_id=sid, defaults=defaults)
        return success({"studentId": sid})

    def post(self, request):
        return self.put(request)

class StudentFileQueryView(BaseView):
    def get(self, request, stu_id):
        try:
            f = StuStudentFile.objects.get(student_id=stu_id)
            return success({k: getattr(f,k) for k in ['student_id','family_info','health_info','award_punish','remark','emergency_contact','update_time']})
        except StuStudentFile.DoesNotExist:
            return success({})

# ---- 课程 ----
class CourseQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaCourse.objects.all()
        if data.get('courseName'):
            qs = qs.filter(course_name__icontains=data['courseName'])
        if data.get('status'):
            qs = qs.filter(status=data['status'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class CourseSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        cid = body.get('courseId') or gen_id('COUR')
        if AcaCourse.objects.filter(course_id=cid).exists():
            AcaCourse.objects.filter(course_id=cid).update(course_name=body.get('courseName'), credit=body.get('credit'), hours=body.get('hours'), dept_id=body.get('deptId'), status=body.get('status','0'))
            # 同步 course_code 若传
            if body.get('courseCode'):
                AcaCourse.objects.filter(course_id=cid).update(course_code=body.get('courseCode'))
            return success({"courseId": cid})
        try:
            c = AcaCourse.objects.create(course_id=cid, course_name=body['courseName'], course_code=body.get('courseCode') or cid, credit=body.get('credit',3), hours=body.get('hours',48), dept_id=body.get('deptId'), status=body.get('status','0'))
        except Exception as e:
            return error(str(e))
        return success({"courseId": c.course_id})

class CourseDeleteView(BaseView):
    def post(self, request, course_id=None):
        cid = course_id or self.parse_body(request).get('courseId') or self.parse_body(request).get('course_id')
        if not cid:
            return error("courseId 不能为空", code=400)
        try:
            c = AcaCourse.objects.get(course_id=cid)
        except AcaCourse.DoesNotExist:
            return error("课程不存在", code=404)
        if AcaScore.objects.filter(course_id=cid).exists():
            return error("该课程存在成绩记录，无法删除，请先删除成绩或标记停用", code=400)
        if AcaEnrollment.objects.filter(course_id=cid, status__in=['0','1']).exists():
            return error("该课程存在有效选课（待缴费/已选），无法删除", code=400)
        if AcaScheduling.objects.filter(course_id=cid).exists():
            # 级联删除排课
            AcaScheduling.objects.filter(course_id=cid).delete()
        c.delete()
        return success()

class CourseSelectableView(BaseView):
    """GET /course/querySelectable?studentId=&semester="""
    def get(self, request):
        student_id = request.GET.get('studentId') or request.GET.get('student_id')
        # 过滤已选、容量、时间冲突简化：仅过滤已选
        enrolled_course_ids = list(AcaEnrollment.objects.filter(student_id=student_id, status__in=['0','1']).values_list('course_id', flat=True))
        qs = AcaCourse.objects.filter(status='0')
        if enrolled_course_ids:
            qs = qs.exclude(course_id__in=enrolled_course_ids)
        lst = list(qs.values())
        return success(lst)

# ---- 排课 ----
class SchedulingSelectView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        qs = AcaScheduling.objects.all()
        if body.get('courseId'):
            qs = qs.filter(course_id=body['courseId'])
        if body.get('teacherId'):
            qs = qs.filter(teacher_id=body['teacherId'])
        if body.get('schedulingDay'):
            qs = qs.filter(scheduling_day=body['schedulingDay'])
        if body.get('sectionType'):
            qs = qs.filter(section_type=body['sectionType'])
        lst = list(qs.values())
        return success(lst)

class SchedulingAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        # update_or_create 按 teacher+day+section 与 room+day+section 唯一
        obj, created = AcaScheduling.objects.update_or_create(
            teacher_id=body['teacherId'],
            scheduling_day=body['schedulingDay'],
            section_type=body['sectionType'],
            defaults={
                'course_id': body.get('courseId'),
                'classroom_id': body.get('classroomId'),
                'scheduling_type': body.get('schedulingType','1'),
            }
        )
        # 额外校验教室冲突
        if AcaScheduling.objects.filter(classroom_id=body.get('classroomId'), scheduling_day=body['schedulingDay'], section_type=body['sectionType']).exclude(id=obj.id).exists():
            return error("教室时间冲突", code=400)
        return success({"id": obj.id})

class SchedulingUpdateView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        sid = body.get('id')
        if not sid:
            return error("id 不能为空", code=400)
        AcaScheduling.objects.filter(id=sid).update(**{k: body[k] for k in body if k in ['course_id','teacher_id','classroom_id','scheduling_day','section_type','scheduling_type']})
        return success()

# ---- 选课 ----
class EnrollmentAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        student_id = body['studentId']
        course_id = body['courseId']
        schedule_id = body.get('scheduleId')
        # 校验是否已选
        if AcaEnrollment.objects.filter(student_id=student_id, course_id=course_id, status__in=['0','1']).exists():
            return error("已选该课程", code=400)
        # 容量校验略（需关联课程容量字段，此处演示直接放行）
        enroll_id = gen_id('ENR')
        AcaEnrollment.objects.create(enroll_id=enroll_id, student_id=student_id, course_id=course_id, schedule_id=schedule_id, status='0')
        return success({"enrollId": enroll_id})

class EnrollmentCancelView(BaseView):
    def post(self, request, enroll_id):
        try:
            en = AcaEnrollment.objects.get(enroll_id=enroll_id)
        except AcaEnrollment.DoesNotExist:
            return error("选课记录不存在", code=404)
        if en.status != '0':
            return error("仅待缴费可退选", code=400)
        en.status = '2'
        en.save(update_fields=['status'])
        return success()

class EnrollmentQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaEnrollment.objects.all()
        if data.get('studentId'):
            qs = qs.filter(student_id=data['studentId'])
        if data.get('courseId'):
            qs = qs.filter(course_id=data['courseId'])
        if data.get('status') is not None:
            qs = qs.filter(status=data['status'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class EnrollmentWorkNumView(BaseView):
    """POST /enrollment/queryWorkNum 按课程聚合选课人数，联表返回课程名（剔除无课程的脏数据）"""
    def post(self, request):
        from django.db.models import Count
        valid_ids = AcaCourse.objects.values_list('course_id', flat=True)
        rows = (AcaEnrollment.objects.filter(status__in=['0','1'], course_id__in=valid_ids)
                .values('course_id').annotate(cnt=Count('enroll_id')).order_by('course_id'))
        name_map = {c.course_id: c.course_name for c in AcaCourse.objects.all()}
        out = [{'courseId': r['course_id'], 'courseName': name_map.get(r['course_id']) or '未知课程', 'cnt': r['cnt']} for r in rows]
        return success(out)

# ---- 考试 ----
class ExamQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaExam.objects.all()
        if data.get('courseId'):
            qs = qs.filter(course_id=data['courseId'])
        total = qs.count()
        lst = list(qs.order_by('-exam_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class ExamAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        eid = body.get('examId') or gen_id('EXAM')
        e = AcaExam.objects.create(exam_id=eid, course_id=body.get('courseId'), exam_name=body.get('examName'), exam_time=body.get('examTime'), paper_id=body.get('paperId'), status=body.get('status','0'))
        return success({"examId": e.exam_id})

# ---- 成绩 ----
class ScoreAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        # GPA 简算：仅分数可改，绩点随分数自动重算
        score = float(body.get('score',0))
        if score >= 90:
            gpa = 4.0
        elif score >= 80:
            gpa = 3.0
        elif score >= 70:
            gpa = 2.0
        elif score >= 60:
            gpa = 1.0
        else:
            gpa = 0.0
        student_id = body['studentId']
        course_id = body['courseId']
        semester = body.get('semester','2024-2025-1')
        # 仅修改分数：若已存在同（学生,课程,学期）则只更新分数/绩点，其他字段不动
        try:
            s = AcaScore.objects.get(student_id=student_id, course_id=course_id, semester=semester)
            s.score = score
            s.gpa_point = gpa
            # 考试ID等保持不动（按需求其他不能动），若传则忽略
            s.save(update_fields=['score','gpa_point'])
            return success({"scoreId": s.score_id, "gpa": float(gpa)})
        except AcaScore.DoesNotExist:
            sid = body.get('scoreId') or gen_id('SCOR')
            s = AcaScore.objects.create(score_id=sid, student_id=student_id, course_id=course_id, semester=semester, exam_id=body.get('examId'), score=score, gpa_point=gpa)
            return success({"scoreId": s.score_id, "gpa": float(gpa)})

class ScoreImportView(BaseView):
    def post(self, request):
        # 需 openpyxl，解析上传 Excel
        try:
            f = request.FILES.get('file')
            if not f:
                return error("请上传文件", code=400)
            import openpyxl
            wb = openpyxl.load_workbook(f)
            ws = wb.active
            count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row or not row[0]:
                    continue
                student_id, course_id, score, semester = row[0], row[1], row[2], (row[3] if len(row)>3 else '2024-2025-1')
                sid = gen_id('SCOR')
                score_val = float(score or 0)
                gpa = 4.0 if score_val>=90 else 3.0 if score_val>=80 else 2.0 if score_val>=70 else 1.0 if score_val>=60 else 0.0
                AcaScore.objects.update_or_create(student_id=str(student_id), course_id=str(course_id), semester=str(semester), defaults={'score_id': sid, 'score': score_val, 'gpa_point': gpa})
                count+=1
            return success({"imported": count})
        except Exception as e:
            return error(str(e))

class ScoreQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaScore.objects.all()
        if data.get('studentId'):
            qs = qs.filter(student_id=data['studentId'])
        if data.get('courseId'):
            qs = qs.filter(course_id=data['courseId'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class ScoreRankView(BaseView):
    def post(self, request):
        from django.db.models import Avg, Count
        data = self.parse_body(request)
        course_id = data.get('courseId')
        qs = AcaScore.objects.all()
        if course_id:
            qs = qs.filter(course_id=course_id)
        # 分数段分布
        buckets = {"90-100": qs.filter(score__gte=90).count(), "80-89": qs.filter(score__gte=80, score__lt=90).count(), "60-79": qs.filter(score__gte=60, score__lt=80).count(), "0-59": qs.filter(score__lt=60).count()}
        avg = qs.aggregate(avg=Avg('score'))['avg']
        return success({"buckets": buckets, "avg": float(avg or 0), "total": qs.count()})

# ---- 班级 ----
class ClassQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = StuClass.objects.all()
        if data.get('className'):
            qs = qs.filter(class_name__icontains=data['className'])
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class ClassSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        cid = body.get('classId') or body.get('class_id')
        if cid:
            StuClass.objects.filter(class_id=cid).update(class_name=body.get('className') or body.get('class_name'), dept_id=body.get('deptId'), grade=body.get('grade'), head_teacher_id=body.get('headTeacherId'))
            return success({"classId": cid})
        c = StuClass.objects.create(class_name=body['className'], dept_id=body.get('deptId'), grade=body.get('grade'), head_teacher_id=body.get('headTeacherId'))
        return success({"classId": c.class_id})

class ClassDeleteView(BaseView):
    def post(self, request, class_id=None):
        cid = class_id or self.parse_body(request).get('classId') or self.parse_body(request).get('class_id')
        if not cid:
            return error("classId 不能为空", code=400)
        StuStudent.objects.filter(class_id=cid).update(class_id=None)
        StuClass.objects.filter(class_id=cid).delete()
        return success()

class StudentDeleteView(BaseView):
    def post(self, request, student_id=None):
        sid = student_id or self.parse_body(request).get('studentId') or self.parse_body(request).get('student_id')
        if not sid:
            return error("studentId 不能为空", code=400)
        try:
            stu = StuStudent.objects.get(student_id=sid)
        except StuStudent.DoesNotExist:
            return error("学生不存在", code=404)
        # 级联清理本库关联
        StuStudentFile.objects.filter(student_id=sid).delete()
        AcaEnrollment.objects.filter(student_id=sid).delete()
        AcaScore.objects.filter(student_id=sid).delete()
        # 清理 resource 库（宿舍分配/借阅）
        try:
            from resource_app.models import ResDormAssign, ResBorrow, ResRoom
            assigns = list(ResDormAssign.objects.using('resource').filter(student_id=sid))
            for a in assigns:
                try:
                    room = ResRoom.objects.using('resource').get(room_id=a.room_id)
                    ResRoom.objects.using('resource').filter(room_id=a.room_id).update(occupied=max(0, room.occupied-1))
                except Exception:
                    pass
            ResDormAssign.objects.using('resource').filter(student_id=sid).delete()
            ResBorrow.objects.using('resource').filter(student_id=sid).delete()
        except Exception:
            pass
        # 清理 finance 库（订单/退款）
        try:
            from finance_app.models import FeeOrder, FeeOrderItem, FeeRefund
            orders = list(FeeOrder.objects.using('finance').filter(student_id=sid))
            oids = [o.order_id for o in orders]
            FeeOrderItem.objects.using('finance').filter(order_id__in=oids).delete()
            FeeRefund.objects.using('finance').filter(order_id__in=oids).delete()
            FeeOrder.objects.using('finance').filter(student_id=sid).delete()
        except Exception:
            pass
        stu.delete()
        return success()

class SchedulingDeleteView(BaseView):
    def post(self, request, id=None):
        sid = id or self.parse_body(request).get('id')
        if not sid:
            return error("id 不能为空", code=400)
        AcaScheduling.objects.filter(id=sid).delete()
        return success()

class EnrollmentUpdateView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        enroll_id = body.get('enrollId') or body.get('enroll_id')
        if not enroll_id:
            return error("enrollId 不能为空", code=400)
        try:
            en = AcaEnrollment.objects.get(enroll_id=enroll_id)
        except AcaEnrollment.DoesNotExist:
            return error("选课记录不存在", code=404)
        if 'scheduleId' in body:
            en.schedule_id = body.get('scheduleId') or None
        if 'status' in body and body['status'] in ('0','1','2','5'):
            en.status = body['status']
        en.save()
        return success({"enrollId": enroll_id})

class ScoreDeleteView(BaseView):
    def post(self, request, score_id=None):
        sid = score_id or self.parse_body(request).get('scoreId') or self.parse_body(request).get('score_id')
        if not sid:
            return error("scoreId 不能为空", code=400)
        AcaScore.objects.filter(score_id=sid).delete()
        return success()
