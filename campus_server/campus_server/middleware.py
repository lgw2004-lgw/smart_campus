import jwt
from django.conf import settings
from django.http import JsonResponse

class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 白名单放行
        path = request.path
        for white in settings.WHITE_LIST:
            if path.startswith(white):
                return self.get_response(request)
        # OPTIONS 放行
        if request.method == 'OPTIONS':
            return self.get_response(request)

        token = request.headers.get('token') or request.headers.get('Token') or request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        if not token:
            # 允许未登录访问的接口由视图自行判断；此处不强制拦截，交由视图校验
            request.user_info = None
            return self.get_response(request)
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            request.user_info = payload
        except Exception:
            request.user_info = None
        return self.get_response(request)
