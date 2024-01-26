from django.urls import path
from .views import *

urlpatterns = [
    path('deploy_test', deploy_test, name='deploy_test'),
    path('login', login, name='login'),
    path('generate_invite_code', generate_invite_code, name='generate_invite_code'),
    path('register', register, name='register'),
    path('add_doctor', add_doctor, name='add_doctor'),
]
