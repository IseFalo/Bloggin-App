from django.urls import path
from . import views

urlpatterns=[
    path('settings/', views.settings, name="settings"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('', views.home, name="home"),
]