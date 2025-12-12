from django.urls import path
from . import views

urlpatterns = [
    path('', views.security_check, name='security_check'),
]