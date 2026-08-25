from utils.base_view import BaseView
from utils.response import success, error, page_response
from utils.pagination import get_page_params
from utils.gen_id import gen_id
from .models import ResBuilding, ResRoom, ResDormAssign, ResBook, ResBorrow, ResDormPublish
from django.db.models import F, Q
import datetime
from django.utils import timezone

def _is_publish_open(college_id=None):
    now = datetime.datetime.now()
    qs = ResDormPublish.objects.filter(is_published='1')
    if college_id is not None:
        qs = qs.filter(Q(college_id__isnull=True) | Q(college_id=college_id))
    qs = qs.filter(Q(start_time__isnull=True) | Q(start_time__lte=now)).filter(Q(end_time__isnull=True) | Q(end_time__gte=now))
    return qs.exists()

def _get_open_college_ids():
    now = datetime.datetime.now()
    pubs = ResDormPublish.objects.filter(is_published='1').filter(Q(start_time__isnull=True) | Q(start_time__lte=now)).filter(Q(end_time__isnull=True) | Q(end_time__gte=now))
    if pubs.filter(college_id__isnull=True).exists():
        return None
    return list(pubs.values_list('college_id', flat=True))

# 宿舍楼栋
class BuildingQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = ResBuilding.objects.all()
        if data.get('buildingName'):
            qs = qs.filter(building_name__icontains=data['buildingName'])
        total = qs.count()
        lst = list(qs.order_by('building_id')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class BuildingSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        bid = body.get('buildingId') or body.get('building_id')
        if bid:
            ResBuilding.objects.filter(building_id=bid).update(building_name=body.get('buildingName'), floors=body.get('floors',6), status=body.get('status','0'))
            return success({"buildingId": bid})
        b = ResBuilding.objects.create(building_name=body['buildingName'], floors=body.get('floors',6), status=body.get('status','0'))
        return success({"buildingId": b.building_id})

class BuildingDeleteView(BaseView):
    def post(self, request, building_id=None):
        bid = building_id or self.parse_body(request).get('buildingId') or self.parse_body(request).get('building_id')
        if not bid:
            return error("buildingId 不能为空", code=400)
        if ResRoom.objects.filter(building_id=bid).exists():
            return error("该楼栋下存在房间，无法删除", code=400)
        ResBuilding.objects.filter(building_id=bid).delete()
        return success()

class RoomSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        room_id = body.get('roomId') or body.get('room_id')
        if room_id:
            ResRoom.objects.filter(room_id=room_id).update(building_id=body.get('buildingId'), room_no=body.get('roomNo'), capacity=body.get('capacity',4), status=body.get('status','0'))
            return success({"roomId": room_id})
        # 校验楼栋
        if not body.get('buildingId') or not body.get('roomNo'):
            return error("楼栋和房号必填", code=400)
        if ResRoom.objects.filter(building_id=body['buildingId'], room_no=body['roomNo']).exists():
            return error("该楼栋下房号已存在", code=400)
        r = ResRoom.objects.create(building_id=body['buildingId'], room_no=body['roomNo'], capacity=body.get('capacity',4), occupied=0, status=body.get('status','0'))
        return success({"roomId": r.room_id})

class RoomDeleteView(BaseView):
    def post(self, request, room_id=None):
        rid = room_id or self.parse_body(request).get('roomId') or self.parse_body(request).get('room_id')
        if not rid:
            return error("roomId 不能为空", code=400)
        if ResDormAssign.objects.filter(room_id=rid).exists():
            return error("该房间已分配学生，无法删除", code=400)
        ResRoom.objects.filter(room_id=rid).delete()
        return success()

class DormQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = ResRoom.objects.all()
        if data.get('shuyuan'):
            bids=list(ResBuilding.objects.filter(building_name__startswith=data['shuyuan']).values_list('building_id', flat=True))
            qs = qs.filter(building_id__in=bids) if bids else qs.none()
        if data.get('collegeId'):
            bids=list(ResBuilding.objects.filter(dept_id=data['collegeId']).values_list('building_id', flat=True))
            qs = qs.filter(building_id__in=bids) if bids else qs.none()
        if data.get('buildingId'):
            qs = qs.filter(building_id=data['buildingId'])
        if data.get('roomNo'):
            qs = qs.filter(room_no__icontains=data['roomNo'])
        if data.get('checkPublish'):
            if not _is_publish_open():
                return page_response([], 0, page_no, page_size)
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class DormAssignView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        student_id = body['studentId']
        building_id = body['buildingId']
        room_id = body['roomId']
        bed_no = body.get('bedNo', 1)
        # 发布校验
        try:
            b = ResBuilding.objects.get(building_id=building_id)
            if not _is_publish_open(b.dept_id):
                return error("宿舍选房未发布或已截止", code=400)
        except ResBuilding.DoesNotExist:
            return error("楼栋不存在", code=404)
        # 校验床位
        try:
            room = ResRoom.objects.get(room_id=room_id)
        except ResRoom.DoesNotExist:
            return error("房间不存在", code=404)
        if room.occupied >= room.capacity:
            return error("床位已满", code=400)
        if ResDormAssign.objects.filter(student_id=student_id).exists():
            return error("学生已分配宿舍", code=400)
        assign_id = gen_id('DORM')
        ResDormAssign.objects.create(assign_id=assign_id, student_id=student_id, building_id=building_id, room_id=room_id, bed_no=bed_no, status='0')
        ResRoom.objects.filter(room_id=room_id).update(occupied=room.occupied+1)
        return success({"assignId": assign_id})

class DormExchangeView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        student_id = body['studentId']
        new_room_id = body['roomId']
        new_building_id = body.get('buildingId')
        # 发布校验
        try:
            nb = ResBuilding.objects.get(building_id=new_building_id or ResRoom.objects.get(room_id=new_room_id).building_id)
            if not _is_publish_open(nb.dept_id):
                return error("宿舍选房未发布或已截止", code=400)
        except Exception:
            pass
        try:
            assign = ResDormAssign.objects.get(student_id=student_id)
        except ResDormAssign.DoesNotExist:
            return error("未分配宿舍", code=404)
        old_room_id = assign.room_id
        # 校验新房
        try:
            new_room = ResRoom.objects.get(room_id=new_room_id)
        except ResRoom.DoesNotExist:
            return error("目标房间不存在", code=404)
        if new_room.occupied >= new_room.capacity:
            return error("目标房间已满", code=400)
        assign.room_id = new_room_id
        if new_building_id:
            assign.building_id = new_building_id
        assign.bed_no = body.get('bedNo', assign.bed_no)
        assign.save(update_fields=['room_id','building_id','bed_no'])
        # 更新计数
        try:
            old = ResRoom.objects.get(room_id=old_room_id)
            ResRoom.objects.filter(room_id=old_room_id).update(occupied=max(0, old.occupied-1))
            ResRoom.objects.filter(room_id=new_room_id).update(occupied=new_room.occupied+1)
        except Exception:
            pass
        return success()

class DormCheckoutView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        student_id = body.get('studentId')
        try:
            assign = ResDormAssign.objects.get(student_id=student_id)
        except ResDormAssign.DoesNotExist:
            return error("未分配宿舍", code=404)
        room_id = assign.room_id
        assign.delete()
        try:
            room = ResRoom.objects.get(room_id=room_id)
            ResRoom.objects.filter(room_id=room_id).update(occupied=max(0, room.occupied-1))
        except Exception:
            pass
        return success()

# 宿舍发布
class DormPublishSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        college_id = body.get('collegeId')
        end_time = body.get('endTime')
        start_time = body.get('startTime')
        is_published = body.get('isPublished') or body.get('is_published') or '1'
        if not end_time:
            return error("结束时间必填", code=400)
        # parse end_time
        try:
            from dateutil import parser as dp
            end_dt = dp.parse(str(end_time))
        except:
            try:
                end_dt = datetime.datetime.strptime(str(end_time), '%Y-%m-%d %H:%M:%S')
            except:
                end_dt = datetime.datetime.strptime(str(end_time), '%Y-%m-%d')
        try:
            start_dt = dp.parse(str(start_time)) if start_time else datetime.datetime.now()
        except:
            start_dt = datetime.datetime.now()
        pid = body.get('publishId')
        if pid:
            ResDormPublish.objects.filter(publish_id=pid).update(college_id=college_id, start_time=start_dt, end_time=end_dt, is_published=is_published)
            return success({"publishId": int(pid)})
        obj = ResDormPublish.objects.create(college_id=college_id, start_time=start_dt, end_time=end_dt, is_published=is_published)
        return success({"publishId": obj.publish_id})

class DormPublishQueryView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = ResDormPublish.objects.all()
        if data.get('collegeId'):
            qs = qs.filter(college_id=data['collegeId'])
        total = qs.count()
        lst = list(qs.order_by('-create_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class DormPublishDeleteView(BaseView):
    def post(self, request, publish_id=None):
        pid = publish_id or self.parse_body(request).get('publishId')
        if not pid:
            return error("publishId必填", code=400)
        ResDormPublish.objects.filter(publish_id=pid).delete()
        return success()

class DormAssignQueryView(BaseView):
    def get(self, request):
        student_id = request.GET.get('studentId') or request.GET.get('student_id')
        if not student_id:
            return error("studentId必填", code=400)
        try:
            assign = ResDormAssign.objects.get(student_id=student_id)
            try:
                building = ResBuilding.objects.get(building_id=assign.building_id)
                building_name = building.building_name
            except:
                building_name = str(assign.building_id)
            try:
                room = ResRoom.objects.get(room_id=assign.room_id)
                room_no = room.room_no
            except:
                room_no = str(assign.room_id)
            return success({"assign_id": assign.assign_id, "building_id": assign.building_id, "building_name": building_name, "room_id": assign.room_id, "room_no": room_no, "bed_no": assign.bed_no})
        except ResDormAssign.DoesNotExist:
            return success(None)

# 图书
class BookQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = ResBook.objects.filter(del_flag='0')
        if data.get('bookName'):
            qs = qs.filter(book_name__icontains=data['bookName'])
        if data.get('category'):
            qs = qs.filter(category=data['category'])
        total = qs.count()
        lst = list(qs[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)

class BookSaveView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        book_id = body.get('bookId') or body.get('book_id')
        if book_id:
            ResBook.objects.filter(book_id=book_id).update(
                book_name=body.get('bookName'),
                isbn=body.get('isbn'),
                author=body.get('author'),
                category=body.get('category'),
                stock=body.get('stock', 0),
                total=body.get('total', body.get('stock', 0)),
            )
            return success({"bookId": book_id})
        try:
            b = ResBook.objects.create(
                book_name=body['bookName'],
                isbn=body.get('isbn'),
                author=body.get('author'),
                category=body.get('category'),
                stock=body.get('stock', 10),
                total=body.get('total', body.get('stock', 10)),
            )
        except Exception as e:
            return error(str(e))
        return success({"bookId": b.book_id})

class BookDeleteView(BaseView):
    def post(self, request, book_id=None):
        bid = book_id or self.parse_body(request).get('bookId') or self.parse_body(request).get('book_id')
        if not bid:
            return error("bookId 不能为空", code=400)
        ResBook.objects.filter(book_id=bid).update(del_flag='1')
        return success()

class BorrowAddView(BaseView):
    def post(self, request):
        body = self.parse_body(request)
        student_id = body['studentId']
        book_id = body['bookId']
        try:
            book = ResBook.objects.get(book_id=book_id)
        except ResBook.DoesNotExist:
            return error("图书不存在", code=404)
        if book.stock <= 0:
            return error("库存不足", code=400)
        borrow_id = gen_id('BORR')
        due = datetime.datetime.now() + datetime.timedelta(days=30)
        ResBorrow.objects.create(borrow_id=borrow_id, student_id=student_id, book_id=book_id, due_time=due, status='0')
        ResBook.objects.filter(book_id=book_id).update(stock=book.stock-1)
        return success({"borrowId": borrow_id, "dueTime": due.strftime('%Y-%m-%d %H:%M:%S')})

class BorrowReturnView(BaseView):
    def post(self, request, borrow_id):
        try:
            br = ResBorrow.objects.get(borrow_id=borrow_id)
        except ResBorrow.DoesNotExist:
            return error("借阅记录不存在", code=404)
        if br.status == '1':
            return error("已归还", code=400)
        br.status = '1'
        br.return_time = datetime.datetime.now()
        # 逾期罚金：超期每天 0.5 元
        if br.due_time and br.return_time > br.due_time:
            days = (br.return_time - br.due_time).days + 1
            br.fine = days * 0.5
        br.save(update_fields=['status','return_time','fine'])
        try:
            book = ResBook.objects.get(book_id=br.book_id)
            ResBook.objects.filter(book_id=br.book_id).update(stock=book.stock+1)
        except Exception:
            pass
        return success({"fine": float(br.fine)})

class BorrowQueryByPageView(BaseView):
    def post(self, request):
        page_no, page_size, data = get_page_params(request)
        qs = ResBorrow.objects.all()
        if data.get('studentId'):
            qs = qs.filter(student_id=data['studentId'])
        if data.get('status'):
            qs = qs.filter(status=data['status'])
        total = qs.count()
        lst = list(qs.order_by('-borrow_time')[(page_no-1)*page_size: page_no*page_size].values())
        return page_response(lst, total, page_no, page_size)


