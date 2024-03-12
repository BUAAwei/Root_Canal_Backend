from django.urls import path
from .views import *

urlpatterns = [
    path('deploy_test', deploy_test, name='deploy_test'),
    path('login', login, name='login'),
    path('generate_invite_code', generate_invite_code, name='generate_invite_code'),
    path('register', register, name='register'),
    path('add_doctor', add_doctor, name='add_doctor'),
    path('get_all_doctors', get_all_doctors, name='get_all_doctors'),
    path('make_doctor_admin', make_doctor_admin, name='make_doctor_admin'),
    path('create_patient', create_patient, name='create_patient'),
    path('delete_patient', delete_patient, name='delete_patient'),
    path('get_all_patient', get_all_patient, name='get_all_patient'),
    path('get_patient_of_doctor', get_patient_of_doctor, name='get_patient_of_doctor'),
    path('upload_slices', upload_slices, name='upload_slices'),
    path('download_stl', download_stl, name='download_stl'),
    path('download_swc', download_swc, name='download_swc'),
]
