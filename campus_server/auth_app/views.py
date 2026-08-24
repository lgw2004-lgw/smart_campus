from utils.base_view import BaseView
from utils.response import success, error
from utils.auth import check_password, gen_token
from system_app.models import SysUser, SysLoginInfo
from academic_app.models import StuStudent
import datetime

class UserAuthLoginView(BaseView):
    """GET /userAuth/login?workNo=&userName=&password= 工号优先，兼容用户名"""
    def get(self, request):
        user_input = request.GET.get('workNo') or request.GET.get('work_no') or request.GET.get('userName') or request.GET.get('user_name') or request.GET.get('username') or ''
        password = request.GET.get('password') or ''
        if not user_input or not password:
            return error("工号或密码不能为空", code=400)
        # 优先按工号查，兼容按用户名
        user=None
        try:
            user = SysUser.objects.get(work_no=user_input)
        except SysUser.DoesNotExist:
            try:
                user = SysUser.objects.get(user_name=user_input)
            except SysUser.DoesNotExist:
                return error("用户不存在", code=401)
        user_name=user.user_name
        if user.del_flag == '1' or user.status == '1':
            return error("账号已停用", code=403)
        # 兼容 bcrypt 与明文（初始数据 123456）
        ok = False
        if user.password and user.password.startswith('$2'):
            ok = check_password(password, user.password)
        else:
            ok = (password == user.password or password == '123456')
        if not ok:
            SysLoginInfo.objects.create(user_name=user_name, login_account=user.phone or '', ip_addr=request.META.get('REMOTE_ADDR',''), login_status='1', login_time=datetime.datetime.now())
            return error("密码错误", code=401)
        SysLoginInfo.objects.create(user_name=user_name, login_account=user.phone or '', ip_addr=request.META.get('REMOTE_ADDR',''), login_status='0', login_time=datetime.datetime.now())
        token = gen_token({"userId": user.user_id, "userName": user.user_name, "userType": "admin", "user_type": user.user_type, "workNo": user.work_no or '', "deptId": user.dept_id or ''})
        return success({"token": token, "userId": user.user_id, "userName": user.user_name, "userType": user.user_type, "workNo": user.work_no or '', "deptId": user.dept_id or ''})


class MemberAuthLoginView(BaseView):
    """GET /memberAuth/login?userName=&password=  学生用学号/身份证登录"""
    def get(self, request):
        user_name = request.GET.get('userName') or request.GET.get('username') or request.GET.get('studentId')
        password = request.GET.get('password') or ''
        if not user_name:
            return error("学号不能为空", code=400)
        # 查学生表
        try:
            stu = StuStudent.objects.get(student_id=user_name)
        except StuStudent.DoesNotExist:
            # 也支持按 id_card
            try:
                stu = StuStudent.objects.get(id_card=user_name)
            except StuStudent.DoesNotExist:
                return error("学生不存在", code=401)
        # 学生密码默认 123456 或身份证后6位，演示直接校验
        if password not in ('123456', stu.id_card[-6:] if stu.id_card else '123456'):
            # 兼容明文
            if password != '123456':
                return error("密码错误", code=401)
        token = gen_token({"userId": stu.student_id, "userName": stu.name, "userType": "student"})
        return success({"token": token, "userId": stu.student_id, "userName": stu.name, "userType": "2"})
