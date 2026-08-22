import json

def get_page_params(request):
    """兼容 {pageNo,pageSize,data:{}} 与 queryString 两种传参"""
    page_no = 1
    page_size = 10
    data = {}
    try:
        if request.method == 'POST' and request.body:
            body = json.loads(request.body.decode('utf-8') or '{}')
            page_no = int(body.get('pageNo') or body.get('pageNum') or 1)
            page_size = int(body.get('pageSize') or 10)
            data = body.get('data') or body.get('query') or {}
            # 兼容直接平铺字段
            if not data:
                # 排除分页字段后剩余即查询条件
                for k in ['pageNo','pageNum','pageSize']:
                    body.pop(k, None)
                body.pop('data', None)
                if body:
                    data = body
        else:
            page_no = int(request.GET.get('pageNo') or request.GET.get('pageNum') or 1)
            page_size = int(request.GET.get('pageSize') or 10)
    except Exception:
        pass
    return page_no, page_size, data
