from django.urls import path
from . import views


urlpatterns=[
    path('settings/', views.settings, name="settings"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name="home"),
    path('like-post/<int:pk>', views.like_post, name="like-post"),
    path('search/', views.search_view, name='search_view'),
    path('create-post', views.create_post, name="create-post"),
    path('drafts', views.drafts_list, name="drafts"),
    path('publish_post/<int:pk>', views.publish_post, name="publish_post"),
    path('post-detail/<int:pk>/', views.post_detail, name="post-detail"),
    path('comment-sent/<int:pk>/', views.comment_sent, name="comment-sent"),
    path('delete-post/<int:pk>/', views.delete_post, name="delete-post"),
    path('edit-post/<int:pk>/', views.edit_post, name="edit-post"),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('create-series/', views.create_series, name='create-series'),
    path('save-post/<int:pk>/', views.save_post, name="save-post"),
    path('add-post-to-series/<int:series_id>/', views.add_post_to_series, name='add-post-to-series'),
    path('series-detail/<int:pk>/', views.series_detail, name='series-detail'),
    path('load-more-posts/<str:username>/', views.load_more, name='load-more-posts'),
    path('add-to-picks/<int:pk>/', views.add_to_picks, name='add_to_picks'),
    path('remove-from-picks/<int:pk>/', views.remove_from_picks, name='remove_from_picks'),
    path('follow/<str:username>/', views.follow, name="follow"),
    path('unfollow/<str:username>/', views.unfollow, name="unfollow"),

    path('get_notifications/', views.get_notifications, name='get_notifications'),

]
