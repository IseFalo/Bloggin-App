from django.urls import path
from . import views

urlpatterns=[
    path('settings/', views.settings, name="settings"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('', views.home, name="home"),
    path('create-post', views.create_post, name="create-post"),
    path('post-detail/<int:pk>/', views.post_detail, name="post-detail"),
    path('delete-post/<int:pk>/', views.delete_post, name="delete-post"),

]