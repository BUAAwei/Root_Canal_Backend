import json
from django.utils.timezone import now
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from django.core.management.utils import get_random_secret_key
from .models import *


@csrf_exempt
@require_http_methods(['POST'])
def deploy_test(request):
    return JsonResponse({'errno': 0, 'ver': "114514", 'cur_time': now()})


@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    data = json.loads(request.body)
    account = data.get('account')
    password = data.get('password')
    if account.find("@") != -1:
        if not Doctor.objects.filter(doctor_mail=account).exists():
            return JsonResponse({'msg': "医生邮箱不存在"})
        doctor = Doctor.objects.get(doctor_mail=account)
    else:
        if not Doctor.objects.filter(doctor_phone=account).exists():
            return JsonResponse({'msg': "医生电话不存在"})
        doctor = Doctor.objects.get(doctor_phone=account)
    if doctor.doctor_password != password:
        return JsonResponse({'msg': f"{doctor.doctor_name}医生密码错误"})
    patients_info = []
    patients = doctor.special_treat_patients.all()
    for patient in patients:
        patient_info = {
            "patient_id": patient.patient_id,
            "patient_name": patient.patient_name,
            "is_data_upload": patient.is_data_upload,
            "description": patient.description
        }
        patients_info.append(patient_info)
    doctor_info = {
        "doctor_id": doctor.doctor_id,
        "doctor_name": doctor.doctor_name,
        "doctor_is_admin": doctor.is_admin,
        "patients_info": patients_info
    }
    return JsonResponse({'msg': "登陆成功", 'doctor_info': doctor_info})


@csrf_exempt
@require_http_methods(['POST'])
def generate_invite_code(request):
    data = json.loads(request.body)
    doctor_is_admin = data.get('is_admin')
    expire_time = data.get('expire_time')
    if not doctor_is_admin:
        return JsonResponse({'msg': "您不是管理员"})
    new_invite_code = InviteCode.objects.create()
    new_invite_code.content = get_random_secret_key()
    new_invite_code.expire_time = now() + timedelta(hours=8+expire_time)
    new_invite_code.save()
    return JsonResponse({
        'msg': "创建邀请码成功",
        'content': new_invite_code.content,
        'expire_time': new_invite_code.expire_time
    })


@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    data = json.loads(request.body)
    code_content = data.get('code_content')
    if not InviteCode.objects.filter(content=code_content).exists():
        return JsonResponse({'msg': "邀请码不存在"})
    invite_code = InviteCode.objects.get(content=code_content)
    if now() + timedelta(hours=8) > invite_code.expire_time:
        return JsonResponse({'msg': "邀请码已过期"})
    name = data.get('name')
    phone = data.get('phone')
    mail = data.get('mail')
    password = data.get('password')
    new_doctor = Doctor.objects.create(doctor_name=name, doctor_phone=phone, doctor_mail=mail, doctor_password=password)
    new_doctor.save()
    return JsonResponse({'msg': "注册成功", 'doctor_id': new_doctor.doctor_id})


@csrf_exempt
@require_http_methods(['POST'])
def add_doctor(request):
    data = json.loads(request.body)
    doctor_is_admin = data.get('is_admin')
    if not doctor_is_admin:
        return JsonResponse({'msg': "您不是管理员"})
    name = data.get('name')
    phone = data.get('phone')
    mail = data.get('mail')
    password = data.get('password')
    new_doctor = Doctor.objects.create(doctor_name=name, doctor_phone=phone, doctor_mail=mail, doctor_password=password)
    new_doctor.save()
    return JsonResponse({'msg': "添加医生成功", 'doctor_id': new_doctor.doctor_id})
