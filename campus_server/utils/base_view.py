from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from utils.response import error

@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):
    def parse_body(self, request):
        if not request.body:
            return {}
        try:
            return json.loads(request.body.decode('utf-8'))
        except Exception:
            return {}

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return error(message=str(e))
