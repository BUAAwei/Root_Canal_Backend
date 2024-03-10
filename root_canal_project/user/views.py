import base64
import json
import os
import shutil

from django.utils.timezone import now
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.response import JsonResponse
from django.core.management.utils import get_random_secret_key
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from root_canal_project import settings
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
            # "left_lower_upload": patient.left_lower_upload,
            # "right_lower_upload": patient.right_lower_upload,
            # "left_upper_upload": patient.left_upper_upload,
            # "right_upper_upload": patient.right_upper_upload,
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
    if phone != "" and Doctor.objects.filter(doctor_phone=phone).exists():
        return JsonResponse({'msg': "当前电话号码已注册"})
    if mail != "" and Doctor.objects.filter(doctor_mail=mail).exists():
        return JsonResponse({'msg': "当前电子邮箱已注册"})
    if phone == "" and mail == "":
        return JsonResponse({'msg': "至少需要输入电话号码与电子邮箱中的一个"})
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
    if phone != "" and Doctor.objects.filter(doctor_phone=phone).exists():
        return JsonResponse({'msg': "当前电话号码已注册"})
    if mail != "" and Doctor.objects.filter(doctor_mail=mail).exists():
        return JsonResponse({'msg': "当前电子邮箱已注册"})
    if phone == "" and mail == "":
        return JsonResponse({'msg': "至少需要输入电话号码与电子邮箱中的一个"})
    new_doctor = Doctor.objects.create(doctor_name=name, doctor_phone=phone, doctor_mail=mail, doctor_password=password)
    new_doctor.save()
    return JsonResponse({'msg': "添加医生成功", 'doctor_id': new_doctor.doctor_id})


@csrf_exempt
@require_http_methods(['POST'])
def get_all_doctors(request):
    doctors = Doctor.objects.all()
    doctors_info = []
    for doctor in doctors:
        doctor_info = {
            "doctor_id": doctor.doctor_id,
            "doctor_name": doctor.doctor_name,
            "doctor_is_admin": doctor.is_admin,
            "doctor_phone": doctor.doctor_phone,
            "doctor_mail": doctor.doctor_mail,
        }
        doctors_info.append(doctor_info)
    return JsonResponse({'doctors_info': doctors_info})


@csrf_exempt
@require_http_methods(['POST'])
def make_doctor_admin(request):
    data = json.loads(request.body)
    doctor_is_admin = data.get('is_admin')
    if not doctor_is_admin:
        return JsonResponse({'msg': "您不是管理员"})
    doctor_id = data.get('doctor_id')
    doctor = Doctor.objects.get(doctor_id=doctor_id)
    doctor.is_admin = True
    doctor.save()
    return JsonResponse({'msg': f"修改{doctor.doctor_name}为管理员成功"})


@csrf_exempt
@require_http_methods(['POST'])
def create_patient(request):
    data = json.loads(request.body)
    doctor_id = data.get('doctor_id')
    doctor = Doctor.objects.get(doctor_id=doctor_id)
    patient_name = data.get('patient_name')
    patient_description = data.get('patient_description')
    new_patient = Patient.objects.create(patient_name=patient_name, description=patient_description)
    new_patient.save()
    doctor.special_treat_patients.add(new_patient)
    return JsonResponse({'msg': f"已向{doctor.doctor_name}医生的病人列表添加{new_patient.patient_name}病人"})


@csrf_exempt
@require_http_methods(['POST'])
def delete_patient(request):
    data = json.loads(request.body)
    patient_id = data.get('patient_id')
    patient = Patient.objects.get(patient_id=patient_id)
    name = patient.patient_name
    patient.delete()
    return JsonResponse({'msg': f"删除病人{name}成功"})


@csrf_exempt
@require_http_methods(['POST'])
def get_all_patient(request):
    patients = Patient.objects.all()
    patients_info = []
    for patient in patients:
        patient_info = {
            "patient_id": patient.patient_id,
            "patient_name": patient.patient_name,
            "description": patient.description,
            # "left_lower_upload": patient.left_lower_upload,
            # "right_lower_upload": patient.right_lower_upload,
            # "left_upper_upload": patient.left_upper_upload,
            # "right_upper_upload": patient.right_upper_upload,
            "is_upload": patient.is_data_upload
        }
        patients_info.append(patient_info)
    return JsonResponse({'patients_info': patients_info})


@csrf_exempt
@require_http_methods(['POST'])
def get_patient_of_doctor(request):
    data = json.loads(request.body)
    doctor_id = data.get('doctor_id')
    doctor = Doctor.objects.get(doctor_id=doctor_id)
    patients = doctor.special_treat_patients.all()
    patients_info = []
    for patient in patients:
        patient_info = {
            "patient_id": patient.patient_id,
            "patient_name": patient.patient_name,
            "description": patient.description,
            # "left_lower_upload": patient.left_lower_upload,
            # "right_lower_upload": patient.right_lower_upload,
            # "left_upper_upload": patient.left_upper_upload,
            # "right_upper_upload": patient.right_upper_upload,
            "is_upload": patient.is_data_upload
        }
        patients_info.append(patient_info)
    return JsonResponse({'patients_info': patients_info})


@csrf_exempt
@require_http_methods(['POST'])
def upload_slices(request):
    files = request.FILES.getlist('files')
    patient_id = request.POST.get('patient_id')
    position = request.POST.get('position')
    patient = Patient.objects.get(patient_id=patient_id)
    new_slices = Slices.objects.create(slices_position=position)
    if patient.is_data_upload:
        patient.teeth_slices.all().delete()
    else:
        patient.is_data_upload = True
    # if position == 'left_lower':
    #     if patient.left_lower_upload:
    #         old_source = patient.teeth_slices.all().filter(slices_position='left_lower')
    #         old_source.all().delete()
    #     else:
    #         patient.left_lower_upload = True
    # elif position == 'left_upper':
    #     if patient.left_upper_upload:
    #         old_source = patient.teeth_slices.all().filter(slices_position='left_upper')
    #         old_source.all().delete()
    #     else:
    #         patient.left_upper_upload = True
    # elif position == 'right_lower':
    #     if patient.right_lower_upload:
    #         old_source = patient.teeth_slices.all().filter(slices_position='right_lower')
    #         old_source.all().delete()
    #     else:
    #         patient.right_lower_upload = True
    # else:
    #     if patient.right_upper_upload:
    #         old_source = patient.teeth_slices.all().filter(slices_position='right_upper')
    #         old_source.all().delete()
    #     else:
    #         patient.right_upper_upload = True
    # if patient.left_lower_upload and patient.left_upper_upload and \
    #         patient.right_lower_upload and patient.right_upper_upload:
    #     patient.is_data_upload = True
    new_slices.save()
    patient.teeth_slices.add(new_slices)
    patient.save()
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    subdir = os.path.join(settings.MEDIA_ROOT, patient_id)
    shutil.rmtree(subdir, ignore_errors=True)
    os.makedirs(subdir, exist_ok=True)
    for file in files:
        fs.save(os.path.join(subdir, file.name), file)
    return JsonResponse({'msg': f"{len(files)}个{position}位置的文件成功上传至病人{patient.patient_name}的资源库中"})


@csrf_exempt
@require_http_methods(['POST'])
def download_stl(request):
    data = json.loads(request.body)
    patient_id = data.get('patient_id')
    # position = data.get('position')
    file_path = os.path.join(settings.BASE_DIR, f'model/{patient_id}/output.stl')
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/stl')
        response['Content-Disposition'] = 'attachment; filename="output.stl"'
        return response
