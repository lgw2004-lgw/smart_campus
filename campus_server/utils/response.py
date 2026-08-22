from django.http import JsonResponse

def success(data=None, message="操作成功"):
    return JsonResponse({"code": 200, "message": message, "data": data}, json_dumps_params={"ensure_ascii": False})

def error(message="操作失败", code=500, data=None):
    return JsonResponse({"code": code, "message": message, "data": data}, json_dumps_params={"ensure_ascii": False})

def page_response(lst, total, page_no, page_size):
    return success({"list": lst, "total": total, "pageNo": page_no, "pageSize": page_size})
