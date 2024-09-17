from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('post/<int:pk>/image/', views.post_image, name='post_image'),
    path('settings/', views.settings, name="settings"),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    # path('', views.home, name="home"),
    path('', views.HomeView.as_view(), name="home"),
    path('like-post/<int:pk>', views.like_post, name="like-post"),
    path('search/results/', views.search_results_view, name='search_results'),
    path('create-post', views.create_post, name="create-post"),
    path('drafts', views.drafts_list, name="drafts"),
    path('publish_post/<int:pk>', views.publish_post, name="publish_post"),
    path('post-detail/<int:pk>/', views.post_detail, name="post-detail"),
    path('comment-sent/<int:pk>/', views.comment_sent, name="comment-sent"),
    path('delete-post/<int:pk>/', views.delete_post, name="delete-post"),
    path('edit-post/<int:pk>/', views.edit_post, name="edit-post"),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile-post-list/<str:username>', views.ProfilePostListView.as_view(), name="profile-post-list"),
    path('create-series/', views.create_series, name='create-series'),
    path('save-post/<int:pk>/', views.save_post, name="save-post"),
    path('saved_posts_list/', views.saved_posts_list, name="saved_posts_list"),
    path('add_post_to_series/<int:post_id>', views.add_post_to_series, name='add_post_to_series'),
    path('series-detail/<int:pk>/', views.series_detail, name='series-detail'),
    path('series-list/<str:username>/', views.SeriesListView.as_view(), name='series-list'),
    path('organization-profile-list/<str:username>/', views.organization_profile_list, name="organization-profile-list"),
    path('organization-profile/<int:pk>/', views.OrganizationProfileView.as_view(), name="organization-profile"),
    path('organization-top-posts', views.organization_top_posts_view, name="organization-top-posts"),
    path('organization-series-list/<int:pk>/', views.organization_series, name="organization-series-list"),
    path('organization-posts-list/<int:pk>/', views.organization_posts_list, name="organization-posts-list"),
    path('add-org-member/<int:user_id>', views.add_org_member, name="add-org-member"),
    path('create-organization-profile', views.create_organization_profile, name="create-organization-profile"),
    path('add-to-picks/<int:pk>/', views.add_to_picks, name='add_to_picks'),
    path('remove-from-picks/<int:pk>/', views.remove_from_picks, name='remove_from_picks'),
    path('follow/<str:username>/', views.follow, name="follow"),
    path('unfollow/<str:username>/', views.unfollow, name="unfollow"),
    path('get_new_notifications/', views.get_notifications, name='get_new_notifications'),
    path('upload-editor-image/', views.upload_editor_image, name='upload_editor_image'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)