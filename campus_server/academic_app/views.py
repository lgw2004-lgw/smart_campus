from utils.base_view import BaseView
from utils.response import success, error, page_response
from utils.pagination import get_page_params
from utils.gen_id import gen_id
from .models import StuStudent, StuStudentFile, StuClass, AcaCourse, AcaScheduling, AcaEnrollment, AcaExam, AcaScore, AcaAttendance
import json

def _get_jwc_college(request):
    """若当前登录为教务处，返回其所属学院dept_id，否则None（管理员看全部）"""
    try:
        from system_app.models import SysUser, SysDept, SysRole, SysRoleUser
        user_id=None
        user_type=None
        # 从中间件注入的user_info取
        info=getattr(request, 'user_info', None)
        if info and isinstance(info, dict):
            user_id=info.get('userId') or info.get('user_id')
            user_type=str(info.get('user_type') or info.get('userType') or '')
        # 尝试从token头解析
        if not user_id:
            token=request.META.get('HTTP_TOKEN') or request.headers.get('token') or ''
            if token:
                try:
                    from utils.auth import decode_token
                    payload=decode_token(token)
                    user_id=payload.get('userId')
                    user_type=str(payload.get('user_type') or payload.get('userType') or '')
                except:
                    pass
        if not user_id:
            return None
        # 判断是否为教务处：user_type 6 或角色含教务
        is_jwc=False
        if str(user_type)=='6':
            is_jwc=True
        else:
            try:
                rids=list(SysRoleUser.objects.filter(user_id=user_id).values_list('role_id', flat=True))
                if rids:
                    for r in SysRole.objects.filter(role_id__in=rids):
                        if '教务' in r.role_name:
                            is_jwc=True
                            break
            except:
                pass
        if not is_jwc:
            return None
        # 取用户所属院系
        try:
            u=SysUser.objects.get(user_id=user_id)
            if not u.dept_id:
                return None
            d=SysDept.objects.get(dept_id=u.dept_id)
            college_id=d.dept_id if d.parent_id==0 else d.parent_id
            return college_id
        except:
            return None
    except:
        return None

def _allowed_dept_ids(college_id):
    if not college_id:
        return None
    try:
        from system_app.models import SysDept
        ids=[college_id]
        for d in SysDept.objects.filter(parent_id=college_id):
            ids.append(d.dept_id)
        return ids
    except:
        return [college_id]

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

class StudentQueryByIdView(BaseView):
    def get(self, request, student_id):
        try:
            stu = StuStudent.objects.get(student_id=student_id)
            data={k: getattr(stu, k) for k in ['student_id','name','sex','id_card','phone','dept_id','class_id','enroll_year','avatar','is_final','create_time']}
            # 关联档案
            try:
                from .models import StuStudentFile
                f=StuStudentFile.objects.get(student_id=student_id)
                data.update({k: getattr(f,k) for k in ['family_info','health_info','award_punish','remark','emergency_contact','emergency_phone']})
            except: pass
            # 学院/专业名
            try:
                from system_app.models import SysDept
                if stu.dept_id:
                    d=SysDept.objects.filter(dept_id=stu.dept_id).first()
                    if d:
                        data['dept_name']=d.dept_name
                        if d.parent_id and d.parent_id!=0:
                            p=SysDept.objects.filter(dept_id=d.parent_id).first()
                            if p: data['college_name']=p.dept_name
                            data['major_name']=d.dept_name
                        else:
                            data['college_name']=d.dept_name
                if stu.class_id:
                    from .models import StuClass
                    c=StuClass.objects.filter(class_id=stu.class_id).first()
                    if c: data['class_name']=c.class_name
            except: pass
            return success(data)
        except StuStudent.DoesNotExist:
            return error("未找到学生", code=404)

class StudentAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        sid = body.get('studentId') or body.get('student_id')
        # 编辑分支：学号已存在则更新
        if sid and StuStudent.objects.filter(student_id=sid).exists():
            # 身份证唯一校验（排除自身）
            id_card = body.get('idCard') or body.get('id_card')
            if id_card and StuStudent.objects.filter(id_card=id_card).exclude(student_id=sid).exists():
                return error("身份证已存在", code=400)
            StuStudent.objects.filter(student_id=sid).update(
                name=body.get('name') or body.get('studentName') or StuStudent.objects.get(student_id=sid).name,
                sex=body.get('sex') if body.get('sex') is not None else StuStudent.objects.get(student_id=sid).sex,
                id_card=id_card if id_card is not None else StuStudent.objects.get(student_id=sid).id_card,
                phone=body.get('phone') if body.get('phone') is not None else StuStudent.objects.get(student_id=sid).phone,
                dept_id=body.get('deptId') if body.get('deptId') is not None else StuStudent.objects.get(student_id=sid).dept_id,
                class_id=body.get('classId') if body.get('classId') is not None else StuStudent.objects.get(student_id=sid).class_id,
                enroll_year=body.get('enrollYear') if body.get('enrollYear') is not None else StuStudent.objects.get(student_id=sid).enroll_year,
                avatar=body.get('avatar') if body.get('avatar') is not None else StuStudent.objects.get(student_id=sid).avatar,
            )
            return success({"studentId": sid})
        # 新增分支
        if not sid:
            sid = gen_id('STU')
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
        # 教务处仅看本学院
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                qs=qs.filter(dept_id__in=allowed)
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
            'emergency_phone': body.get('emergencyPhone') or body.get('emergency_phone'),
        }
        obj, created = StuStudentFile.objects.update_or_create(student_id=sid, defaults=defaults)
        return success({"studentId": sid})

    def post(self, request):
        return self.put(request)

class StudentFileQueryView(BaseView):
    def get(self, request, stu_id):
        try:
            f = StuStudentFile.objects.get(student_id=stu_id)
            return success({k: getattr(f,k) for k in ['student_id','family_info','health_info','award_punish','remark','emergency_contact','emergency_phone','update_time']})
        except StuStudentFile.DoesNotExist:
            return success({})

# ---- 课程 ----
class CourseQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaCourse.objects.all()
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                qs=qs.filter(dept_id__in=allowed)
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
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                allowed_courses=list(AcaCourse.objects.filter(dept_id__in=allowed).values_list('course_id', flat=True))
                qs=qs.filter(course_id__in=allowed_courses)
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
        def gv(camel, snake): return body.get(camel) if body.get(camel) is not None else body.get(snake)
        teacher_id = gv('teacherId','teacher_id')
        scheduling_day = gv('schedulingDay','scheduling_day')
        section_type = gv('sectionType','section_type')
        course_id = gv('courseId','course_id')
        classroom_id = gv('classroomId','classroom_id')
        scheduling_type = gv('schedulingType','scheduling_type') or '1'
        if not teacher_id or not scheduling_day or not section_type:
            return error("teacherId/schedulingDay/sectionType必填", code=400)
        obj, created = AcaScheduling.objects.update_or_create(
            teacher_id=teacher_id,
            scheduling_day=scheduling_day,
            section_type=section_type,
            defaults={
                'course_id': course_id,
                'classroom_id': classroom_id,
                'scheduling_type': scheduling_type,
            }
        )
        if classroom_id and AcaScheduling.objects.filter(classroom_id=classroom_id, scheduling_day=scheduling_day, section_type=section_type).exclude(id=obj.id).exists():
            return error("教室时间冲突", code=400)
        return success({"id": obj.id})

class SchedulingUpdateView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        sid = body.get('id')
        if not sid:
            return error("id 不能为空", code=400)
        # 兼容 camel/snake 双命名
        mapping = {'courseId':'course_id','course_id':'course_id','teacherId':'teacher_id','teacher_id':'teacher_id','classroomId':'classroom_id','classroom_id':'classroom_id','schedulingDay':'scheduling_day','scheduling_day':'scheduling_day','sectionType':'section_type','section_type':'section_type','schedulingType':'scheduling_type','scheduling_type':'scheduling_type'}
        upd={}
        for k,v in body.items():
            if k in mapping:
                upd[mapping[k]]=v
        if upd:
            AcaScheduling.objects.filter(id=sid).update(**upd)
        return success()

# ---- 选课 ----
class EnrollmentAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        student_id = body.get('studentId') or body.get('student_id')
        course_id = body.get('courseId') or body.get('course_id')
        schedule_id = body.get('scheduleId') or body.get('schedule_id')
        if not student_id or not course_id:
            return error("studentId与courseId必填", code=400)
        try:
            stu = StuStudent.objects.get(student_id=student_id)
            if stu.is_final == '1':
                return error("课程已完成，无法重复修读（已归档）", code=400)
        except StuStudent.DoesNotExist:
            return error("学生不存在", code=404)
        try:
            crs = AcaCourse.objects.get(course_id=course_id)
            if crs.status == '1':
                return error("课程已停用，无法选课", code=400)
        except AcaCourse.DoesNotExist:
            return error("课程不存在", code=404)
        if AcaEnrollment.objects.filter(student_id=student_id, course_id=course_id, status__in=['0','1']).exists():
            return error("已选该课程", code=400)
        # 总学费校验：需先缴纳当前学期总学费（TUITION 订单已付）
        try:
            from finance_app.models import FeeOrder, FeeTuitionConfig, FeeOrderItem
            cfg = FeeTuitionConfig.objects.order_by('-create_time').first()
            if cfg:
                sem = cfg.semester
                has_tuition = FeeOrder.objects.filter(student_id=student_id, semester=sem, order_type='TUITION', order_status='3').exists()
                if not has_tuition:
                    # 未缴总学费禁止选课（重修也需先缴总学费）
                    return error(f"请先缴纳 {sem} 总学费", code=400)
        except Exception:
            pass
        # 是否重修：已有成绩即视为重修（需另缴重修费）
        is_retake = AcaScore.objects.filter(student_id=student_id, course_id=course_id).exists()
        enroll_id = gen_id('ENR')
        AcaEnrollment.objects.create(enroll_id=enroll_id, student_id=student_id, course_id=course_id, schedule_id=schedule_id, status='0')
        if is_retake:
            # 自动计算重修费并生成 RETAKE 订单（待付）
            try:
                from finance_app.models import FeeOrder, FeeOrderItem
                price = float(crs.credit or 3) * 100
                order_id = gen_id('ORD')
                sem = cfg.semester if 'cfg' in locals() and cfg else '2024-2025-1'
                FeeOrder.objects.create(order_id=order_id, student_id=student_id, order_amount=price, order_status='0', order_type='RETAKE', semester=sem, ch_id=enroll_id, detail=f"重修 {crs.course_name}")
                FeeOrderItem.objects.create(item_id=gen_id('ITEM'), order_id=order_id, ref_id=enroll_id, item_name=f"重修-{crs.course_name}", item_price=price, item_num=1, item_amount=price)
                return success({"enrollId": enroll_id, "isRetake": True, "retakeFee": price, "retakeOrderId": order_id})
            except Exception as e:
                return success({"enrollId": enroll_id, "isRetake": True, "retakeFeeError": str(e)})
        return success({"enrollId": enroll_id, "isRetake": False})

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
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                allowed_courses=list(AcaCourse.objects.filter(dept_id__in=allowed).values_list('course_id', flat=True))
                qs=qs.filter(course_id__in=allowed_courses)
        if data.get('studentId'):
            qs = qs.filter(student_id=data['studentId'])
        if data.get('courseId'):
            qs = qs.filter(course_id=data['courseId'])
        if data.get('status') not in (None, '') :
            qs = qs.filter(status=data['status'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class EnrollmentWorkNumView(BaseView):
    """POST /enrollment/queryWorkNum 按课程聚合选课人数，联表返回课程名（剔除无课程的脏数据）"""
    def post(self, request):
        from django.db.models import Count
        valid_ids = AcaCourse.objects.values_list('course_id', flat=True)
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                valid_ids = AcaCourse.objects.filter(dept_id__in=allowed).values_list('course_id', flat=True)
        rows = (AcaEnrollment.objects.filter(status__in=['0','1'], course_id__in=valid_ids)
                .values('course_id').annotate(cnt=Count('enroll_id')).order_by('course_id'))
        # name_map按学院过滤
        if college and allowed is not None:
            name_map = {c.course_id: c.course_name for c in AcaCourse.objects.filter(dept_id__in=allowed)}
        else:
            name_map = {c.course_id: c.course_name for c in AcaCourse.objects.all()}
        out = [{'courseId': r['course_id'], 'courseName': name_map.get(r['course_id']) or '未知课程', 'cnt': r['cnt']} for r in rows]
        return success(out)

# ---- 考试 ----
class ExamQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaExam.objects.all()
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                allowed_courses=list(AcaCourse.objects.filter(dept_id__in=allowed).values_list('course_id', flat=True))
                qs=qs.filter(course_id__in=allowed_courses)
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
        # GPA 简算
        try:
            score = float(body.get('score',0))
        except:
            return error("score 非法", code=400)
        if score >= 90: gpa = 4.0
        elif score >= 80: gpa = 3.0
        elif score >= 70: gpa = 2.0
        elif score >= 60: gpa = 1.0
        else: gpa = 0.0
        student_id = body.get('studentId') or body.get('student_id')
        course_id = body.get('courseId') or body.get('course_id')
        semester = body.get('semester','2024-2025-1')
        exam_type = str(body.get('examType') or body.get('exam_type') or '0')
        if not student_id or not course_id:
            return error("studentId与courseId必填", code=400)
        # 必须已选且已缴费(status=1)才能录分（防未缴费/未选课幽灵分）
        if not AcaEnrollment.objects.filter(student_id=student_id, course_id=course_id, status='1').exists():
            return error("该生未选课或未缴费，无考试资格", code=400)
        # 补考/重修历史保留：exam_type 0正常 1补考 2重修，is_retake标记
        is_retake = '1' if exam_type in ('1','2') else '0'
        # 同(学生,课程,学期,exam_type)已存在则更新，否则创建
        # 若exam_type为0且已存在，视为首考更新；若为1/2则保留原0记录，新增1条
        try:
            s = AcaScore.objects.get(student_id=student_id, course_id=course_id, semester=semester, exam_type=exam_type)
            # 已存在同类型：仅允许更新分数（幂等）
            s.score = score
            s.gpa_point = gpa
            s.is_retake = is_retake
            s.exam_id = body.get('examId') or s.exam_id
            s.save(update_fields=['score','gpa_point','is_retake','exam_id','update_time'])
            return success({"scoreId": s.score_id, "gpa": float(gpa), "is_retake": s.is_retake})
        except AcaScore.DoesNotExist:
            # 若是补考/重修，需确保原首考记录存在（挂科历史）
            if is_retake=='1' and not AcaScore.objects.filter(student_id=student_id, course_id=course_id, semester=semester, exam_type='0').exists():
                # 允许直接创建补考但标记
                pass
            sid = body.get('scoreId') or body.get('score_id') or gen_id('SCOR')
            s = AcaScore.objects.create(score_id=sid, student_id=student_id, course_id=course_id, semester=semester, exam_type=exam_type, is_retake=is_retake, exam_id=body.get('examId'), score=score, gpa_point=gpa)
            return success({"scoreId": s.score_id, "gpa": float(gpa), "is_retake": is_retake})

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
                exam_type = str(row[4] if len(row)>4 and row[4] else '0')
                is_retake = '1' if exam_type!='0' else '0'
                sid = gen_id('SCOR')
                score_val = float(score or 0)
                gpa = 4.0 if score_val>=90 else 3.0 if score_val>=80 else 2.0 if score_val>=70 else 1.0 if score_val>=60 else 0.0
                # 需已选校验略，导入时仅告警
                AcaScore.objects.update_or_create(student_id=str(student_id), course_id=str(course_id), semester=str(semester), exam_type=exam_type, defaults={'score_id': sid, 'score': score_val, 'gpa_point': gpa, 'is_retake': is_retake})
                count+=1
            return success({"imported": count})
        except Exception as e:
            return error(str(e))

class ScoreQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaScore.objects.all()
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                allowed_courses=list(AcaCourse.objects.filter(dept_id__in=allowed).values_list('course_id', flat=True))
                qs=qs.filter(course_id__in=allowed_courses)
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
        college=_get_jwc_college(request)
        if college:
            allowed=_allowed_dept_ids(college)
            if allowed is not None:
                qs=qs.filter(dept_id__in=allowed)
        if data.get('className'):
            qs = qs.filter(class_name__icontains=data['className'])
        total = qs.count()
        lst = list(qs.order_by('head_teacher_id','class_name')[(page_no-1)*page_size: page_no*page_size].values())
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

class StudentArchiveView(BaseView):
    """POST /student/archive {studentId} 成绩→归档，需校验（如学分/GPA）此处简化为需至少1条成绩"""
    def post(self, request):
        body = self.parse_body(request)
        sid = body.get('studentId') or body.get('student_id')
        if not sid:
            return error("studentId 不能为空", code=400)
        try:
            stu = StuStudent.objects.get(student_id=sid)
        except StuStudent.DoesNotExist:
            return error("学生不存在", code=404)
        if stu.is_final == '1':
            return error("已归档", code=400)
        if not AcaScore.objects.filter(student_id=sid).exists():
            return error("无成绩记录，无法归档", code=400)
        stu.is_final = '1'
        stu.save(update_fields=['is_final'])
        return success({"studentId": sid, "is_final": "1"})

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
        if 'status' in body and body['status'] is not None and body['status'] != '':
            new_status = str(body['status'])
            # 仅允许 0→2 退选，其他变迁需走缴费/退费专用接口
            allowed = {('0','2')}
            if (en.status, new_status) not in allowed:
                return error(f"非法的状态流转 {en.status}→{new_status}，仅允许 0→2", code=400)
            en.status = new_status
        en.save()
        return success({"enrollId": enroll_id})

class ScoreDeleteView(BaseView):
    def post(self, request, score_id=None):
        sid = score_id or self.parse_body(request).get('scoreId') or self.parse_body(request).get('score_id')
        if not sid:
            return error("scoreId 不能为空", code=400)
        AcaScore.objects.filter(score_id=sid).delete()
        return success()

class AttendanceMarkView(BaseView):
    """POST /attendance/mark {studentId,courseId,scheduleId} 缴费后才能上课"""
    def post(self, request):
        body = self.parse_body(request)
        sid = body.get('studentId') or body.get('student_id')
        cid = body.get('courseId') or body.get('course_id')
        sch_id = body.get('scheduleId') or body.get('schedule_id')
        if not sid or not cid:
            return error("studentId与courseId必填", code=400)
        # 必须已选且已缴费 status=1
        if not AcaEnrollment.objects.filter(student_id=sid, course_id=cid, status='1').exists():
            return error("未缴费或未选课，禁止上课（需先完成缴费 status=1）", code=400)
        # 退选后也禁止
        if AcaEnrollment.objects.filter(student_id=sid, course_id=cid, status='2').exists():
            return error("已退选，无上课资格", code=400)
        att = AcaAttendance.objects.create(student_id=sid, course_id=cid, schedule_id=sch_id, attend_status='1')
        return success({"attendanceId": att.id})

class AttendanceQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = AcaAttendance.objects.all()
        if data.get('studentId'): qs = qs.filter(student_id=data['studentId'])
        if data.get('courseId'): qs = qs.filter(course_id=data['courseId'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)
