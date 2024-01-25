import os
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse


@csrf_exempt
@require_http_methods(['POST'])
def deploy_test(request):
    return JsonResponse({'errno': 0, 'ver': "114514", 'cur_time': now()})

# Create your views here.
