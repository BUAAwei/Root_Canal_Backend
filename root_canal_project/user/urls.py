from django.urls import path
from .views import *

urlpatterns = [
    path('deploy_test', deploy_test, name='deploy_test'),
]
