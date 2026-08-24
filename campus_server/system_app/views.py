import json
from utils.base_view import BaseView
from utils.response import success, error, page_response
from utils.pagination import get_page_params
from utils.gen_id import gen_id
from utils.auth import hash_password
from .models import (
    SysUser, SysRole, SysRoleUser, SysMenu, SysRoleMenu,
    SysDept, SysDictType, SysDictData, SysNotice, HealthNews, HosBanner,
    SysLoginInfo, SysOperLog
)

# -------- 用户 --------
class UserQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysUser.objects.filter(del_flag='0')
        if data.get('userName'):
            qs = qs.filter(user_name__icontains=data['userName'])
        if data.get('status'):
            qs = qs.filter(status=data['status'])
        if data.get('userType') or data.get('user_type'):
            qs = qs.filter(user_type=str(data.get('userType') or data.get('user_type')))
        if data.get('deptId') or data.get('dept_id'):
            try:
                qs = qs.filter(dept_id=int(data.get('deptId') or data.get('dept_id')))
            except:
                pass
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class UserInsertOrUpdateView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        user_id = body.get('userId') or body.get('user_id')
        work_no = body.get('workNo') or body.get('work_no')
        if user_id:
            # 工号唯一校验
            if work_no and SysUser.objects.filter(work_no=work_no).exclude(user_id=user_id).exists():
                return error("工号已存在", code=400)
            upd={}
            if body.get('userName') is not None or body.get('user_name') is not None:
                upd['user_name']=body.get('userName', body.get('user_name'))
            if work_no is not None:
                upd['work_no']=work_no
            if body.get('phone') is not None:
                upd['phone']=body.get('phone')
            if body.get('deptId') is not None or body.get('dept_id') is not None:
                upd['dept_id']=body.get('deptId') or body.get('dept_id')
            if body.get('status') is not None:
                upd['status']=body.get('status')
            if body.get('userType') is not None or body.get('user_type') is not None:
                upd['user_type']=body.get('userType') or body.get('user_type')
            if upd:
                SysUser.objects.filter(user_id=user_id).update(**upd)
            if body.get('password'):
                u = SysUser.objects.get(user_id=user_id)
                u.password = hash_password(body['password'])
                u.save(update_fields=['password'])
            return success({"userId": user_id})
        # 新增
        if work_no and SysUser.objects.filter(work_no=work_no).exists():
            return error("工号已存在", code=400)
        pwd = body.get('password') or '123456'
        hashed = hash_password(pwd) if len(pwd) < 50 else pwd
        u = SysUser.objects.create(
            user_name=body['userName'],
            work_no=work_no,
            phone=body.get('phone'),
            dept_id=body.get('deptId'),
            user_type=body.get('userType','0'),
            password=hashed,
            status=body.get('status','0'),
        )
        # 若未传工号自动生成 GH+id
        if not u.work_no:
            u.work_no=f"GH{u.user_id:04d}"
            u.save(update_fields=['work_no'])
        return success({"userId": u.user_id, "workNo": u.work_no})

class UserSaveView(BaseView):
    """POST /user/save 分配角色 {userId, roleIds:[]}"""
    def post(self, request):
        body = self.parse_body(request)
        user_id = body.get('userId') or body.get('user_id')
        role_ids = body.get('roleIds') or body.get('role_ids') or []
        SysRoleUser.objects.filter(user_id=user_id).delete()
        for rid in role_ids:
            SysRoleUser.objects.create(user_id=user_id, role_id=rid)
        return success()

class UserDeleteView(BaseView):
    def post(self, request, user_id=None):
        # 支持 /user/delete/{id} 或 body
        uid = user_id or self.parse_body(request).get('userId')
        SysUser.objects.filter(user_id=uid).update(del_flag='1')
        return success()

# -------- 角色 --------
class RoleQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysRole.objects.all()
        if data.get('roleName'):
            qs = qs.filter(role_name__icontains=data['roleName'])
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class RoleSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        role_id = body.get('roleId') or body.get('role_id')
        if role_id:
            SysRole.objects.filter(role_id=role_id).update(role_name=body.get('roleName'), role_code=body.get('roleCode'), status=body.get('status','0'))
            return success({"roleId": role_id})
        # 校验编码唯一
        if body.get('roleCode') and SysRole.objects.filter(role_code=body.get('roleCode')).exists():
            return error("角色编码已存在", code=400)
        r = SysRole.objects.create(role_name=body['roleName'], role_code=body.get('roleCode') or f"role:{body['roleName']}", status=body.get('status','0'))
        return success({"roleId": r.role_id})

class RoleDeleteView(BaseView):
    def post(self, request, role_id=None):
        rid = role_id or self.parse_body(request).get('roleId') or self.parse_body(request).get('role_id')
        if not rid:
            return error("roleId 不能为空", code=400)
        if SysRoleUser.objects.filter(role_id=rid).exists():
            return error("该角色已分配给用户，无法删除", code=400)
        SysRole.objects.filter(role_id=rid).delete()
        SysRoleMenu.objects.filter(role_id=rid).delete()
        return success()

class RoleMenuAddView(BaseView):
    """POST /role/roleMenu/add {roleId, menuIds}"""
    def post(self, request):
        body = self.parse_body(request)
        role_id = body.get('roleId') or body.get('role_id')
        menu_ids = body.get('menuIds') or body.get('menu_ids') or []
        SysRoleMenu.objects.filter(role_id=role_id).delete()
        for mid in menu_ids:
            SysRoleMenu.objects.create(role_id=role_id, menu_id=mid)
        return success()

# -------- 菜单 --------
class MenuTreeView(BaseView):
    """GET /menu/queryTreeDataByUserId?userId="""
    def get(self, request):
        user_id = request.GET.get('userId') or request.GET.get('user_id')
        if user_id:
            role_ids = list(SysRoleUser.objects.filter(user_id=user_id).values_list('role_id', flat=True))
            menu_ids = list(SysRoleMenu.objects.filter(role_id__in=role_ids).values_list('menu_id', flat=True)) if role_ids else []
            qs = SysMenu.objects.filter(menu_id__in=menu_ids) if menu_ids else SysMenu.objects.all()
        else:
            qs = SysMenu.objects.all()
        menus = list(qs.order_by('sort').values())
        # 组树
        def build_tree(pid=0):
            res=[]
            for m in [x for x in menus if x['parent_id']==pid]:
                children=build_tree(m['menu_id'])
                node={**m, "children": children}
                res.append(node)
            return res
        return success(build_tree(0))

class MenuSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        menu_id = body.get('menuId') or body.get('menu_id')
        if menu_id:
            SysMenu.objects.filter(menu_id=menu_id).update(
                menu_name=body.get('menuName'),
                parent_id=body.get('parentId', 0),
                path=body.get('path'),
                icon=body.get('icon'),
                sort=body.get('sort', 0),
            )
            return success({"menuId": menu_id})
        m = SysMenu.objects.create(
            menu_name=body['menuName'],
            parent_id=body.get('parentId', 0),
            path=body.get('path'),
            icon=body.get('icon'),
            sort=body.get('sort', 0),
        )
        return success({"menuId": m.menu_id})

class MenuDeleteView(BaseView):
    def post(self, request, menu_id=None):
        mid = menu_id or self.parse_body(request).get('menuId') or self.parse_body(request).get('menu_id')
        if not mid:
            return error("menuId 不能为空", code=400)
        if SysMenu.objects.filter(parent_id=mid).exists():
            return error("该菜单存在下级，无法删除", code=400)
        SysRoleMenu.objects.filter(menu_id=mid).delete()
        SysMenu.objects.filter(menu_id=mid).delete()
        return success()

# -------- 院系 --------
class DeptQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysDept.objects.all()
        if data.get('deptName'):
            qs = qs.filter(dept_name__icontains=data['deptName'])
        if data.get('deptId'):
            qs = qs.filter(dept_id=data['deptId'])
        if data.get('parentId') is not None and data.get('parentId') != '':
            try:
                qs = qs.filter(parent_id=int(data['parentId']))
            except:
                pass
        total = qs.count()
        lst = list(qs.order_by('order_num')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class DeptSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        dept_id = body.get('deptId') or body.get('dept_id')
        if dept_id:
            SysDept.objects.filter(dept_id=dept_id).update(dept_name=body.get('deptName'), parent_id=body.get('parentId',0), order_num=body.get('orderNum',0), status=body.get('status','0'))
            return success({"deptId": dept_id})
        parent_id = body.get('parentId',0) or 0
        # 专业ID规则：所属学院id+001/002...（如 1→1001、4→4001），学院顶级仍走自增
        if parent_id != 0:
            try:
                parent = SysDept.objects.get(dept_id=parent_id)
                if parent.parent_id == 0:
                    existing = list(SysDept.objects.filter(parent_id=parent_id).values_list('dept_id', flat=True))
                    seq = len(existing) + 1
                    new_id = parent_id * 1000 + seq
                    while SysDept.objects.filter(dept_id=new_id).exists():
                        seq += 1
                        new_id = parent_id * 1000 + seq
                    d = SysDept.objects.create(dept_id=new_id, dept_name=body['deptName'], parent_id=parent_id, order_num=body.get('orderNum',0))
                    return success({"deptId": d.dept_id})
            except SysDept.DoesNotExist:
                print(f"[DeptSave] parent {parent_id} not found")
                pass
        d = SysDept.objects.create(dept_name=body['deptName'], parent_id=parent_id, order_num=body.get('orderNum',0))
        return success({"deptId": d.dept_id})

class DeptDeleteView(BaseView):
    def post(self, request, dept_id=None):
        did = dept_id or self.parse_body(request).get('deptId') or self.parse_body(request).get('dept_id')
        if not did:
            return error("deptId 不能为空", code=400)
        if SysDept.objects.filter(parent_id=did).exists():
            return error("该院系存在下级，无法删除", code=400)
        if SysUser.objects.filter(dept_id=did, del_flag='0').exists():
            return error("该院系下存在用户，无法删除", code=400)
        SysDept.objects.filter(dept_id=did).delete()
        return success()

class DeptTreeView(BaseView):
    def get(self, request):
        # 返回 学院-专业 二级树（单校，已去掉学校层）
        depts = list(SysDept.objects.all().order_by('order_num').values())
        def build(pid):
            res=[]
            for d in [x for x in depts if x['parent_id']==pid]:
                children=build(d['dept_id'])
                level=0
                p=d['parent_id']
                while p!=0:
                    level+=1
                    parent=next((x for x in depts if x['dept_id']==p), None)
                    p=parent['parent_id'] if parent else 0
                label='学院' if level==0 else '专业'
                node={**d, 'children': children, 'level': level, 'levelLabel': label}
                res.append(node)
            return res
        return success(build(0))

# -------- 字典 --------
class DictTypeQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysDictType.objects.all()
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class DictDataQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysDictData.objects.all()
        if data.get('dictType'):
            qs = qs.filter(dict_type=data['dictType'])
        total = qs.count()
        lst = list(qs.order_by('dict_sort')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class DictDataByTypeView(BaseView):
    def get(self, request, dict_type):
        lst = list(SysDictData.objects.filter(dict_type=dict_type, status='0').order_by('dict_sort').values())
        return success(lst)

# -------- 公告/资讯/轮播 --------
class NoticeQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysNotice.objects.all()
        if data.get('noticeTitle'):
            qs = qs.filter(notice_title__icontains=data['noticeTitle'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class NoticeSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        nid = body.get('noticeId')
        if nid:
            SysNotice.objects.filter(notice_id=nid).update(notice_title=body.get('noticeTitle'), notice_content=body.get('noticeContent'), notice_type=body.get('noticeType','1'), status=body.get('status','0'))
            return success({"noticeId": nid})
        n = SysNotice.objects.create(notice_title=body['noticeTitle'], notice_content=body.get('noticeContent'), notice_type=body.get('noticeType','1'))
        return success({"noticeId": n.notice_id})

class NoticeDeleteView(BaseView):
    def post(self, request, notice_id=None):
        nid = notice_id or self.parse_body(request).get('noticeId') or self.parse_body(request).get('notice_id')
        if not nid:
            return error("noticeId 不能为空", code=400)
        SysNotice.objects.filter(notice_id=nid).delete()
        return success()

class NewsQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = HealthNews.objects.all()
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class BannerQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = HosBanner.objects.filter(deleted=0)
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class BannerSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        bid = body.get('id')
        if bid:
            HosBanner.objects.filter(id=bid).update(name=body.get('name'), url=body.get('url'), position=body.get('position',0), enabled=1 if body.get('enabled') else 0)
            return success({"id": bid})
        b = HosBanner.objects.create(name=body['name'], url=body.get('url'), position=body.get('position',0), enabled=1 if body.get('enabled') else 0)
        return success({"id": b.id})

class BannerUploadView(BaseView):
    """POST /banner/upload multipart file -> 保存到 media/banner 返回URL"""
    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return error("请选择文件", code=400)
        import os, uuid, datetime
        from django.conf import settings
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'):
            return error("仅支持图片文件(png/jpg/jpeg/gif/webp/bmp)", code=400)
        sub = 'banner'
        d = settings.MEDIA_ROOT / sub
        os.makedirs(d, exist_ok=True)
        fname = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:6] + ext
        path = d / fname
        with open(path, 'wb') as fp:
            for chunk in f.chunks():
                fp.write(chunk)
        rel = f"{settings.MEDIA_URL}{sub}/{fname}"
        port = request.META.get('SERVER_PORT', '18367')
        full = f"http://127.0.0.1:{port}{rel}"
        return success({"url": full, "relative": rel, "name": fname})

class BannerDeleteView(BaseView):
    def post(self, request, id=None):
        bid = id or self.parse_body(request).get('id')
        if not bid:
            return error("id 不能为空", code=400)
        HosBanner.objects.filter(id=bid).update(deleted=1)
        return success()

class BannerLoadView(BaseView):
    def get(self, request):
        lst = list(HosBanner.objects.filter(enabled=1, deleted=0).order_by('position').values())
        return success(lst)

# -------- 日志 --------
class LoginInfoQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysLoginInfo.objects.all()
        total = qs.count()
        lst = list(qs.order_by('-login_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class OperLogQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = SysOperLog.objects.all()
        total = qs.count()
        lst = list(qs.order_by('-oper_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)
