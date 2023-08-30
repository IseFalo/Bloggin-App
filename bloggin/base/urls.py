from django.urls import path
from . import views

urlpatterns=[
    path('settings/', views.settings, name="settings"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name="home"),
    path('create-post', views.create_post, name="create-post"),
    path('post-detail/<int:pk>/', views.post_detail, name="post-detail"),
    path('delete-post/<int:pk>/', views.delete_post, name="delete-post"),
    path('edit-post/<int:pk>/', views.edit_post, name="edit-post"),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('add-to-picks/<int:pk>/', views.add_to_picks, name='add_to_picks'),
    path('remove-from-picks/<int:pk>/', views.remove_from_picks, name='remove_from_picks'),
    path('follow/<str:username>/', views.follow, name="follow"),
    path('unfollow/<str:username>/', views.unfollow, name="unfollow"),
    
]