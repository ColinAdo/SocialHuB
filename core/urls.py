from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

# app_name='core'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('verifications/', views.codeVerification, name='code_verification'),
    path('signout/', views.signout, name='signout'),

    path('settings/', views.settings, name='settings'),
    path('uploadpost/', views.uploadpost, name='uploadpost'),
    path('delete/post/<str:pk>/', views.deletepost, name='deletepost'),

    path('likepost/', views.likePost, name='likepost'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile-posts/<str:username>/<uuid:post_id>/', views.profile_posts, name='profileposts'),
    path('followunfollow/', views.followunfollow, name='followunfollow'),

    path('search/', views.search, name='search'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),

    path('password-change/', views.custom_password_change, name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'), name='password_change_done'),

    path('comment/<str:pk>/', views.comments, name='comment'),
    path('delete/comment/<str:pk>/', views.deletecomment, name='deletecomment'),

    path('message/<str:receiver_username>/', views.send_message, name='message'),
    path('delete/message/<str:pk>/', views.deletemessage, name='deletemessage'),

    path('inbox/', views.inbox, name='inbox'),
    path("update_notification_count/", views.update_notification_count, name="update_notification_count"),
    path('delete/inbox/<str:message_id>/', views.deleteinbox, name='deleteinbox'),

    path('<str:username>/followers-list/', views.followers_list, name='followers-list'),
    path('<str:username>/following-list/', views.following_list, name='following-list'),
    path('back-to-page/', views.back_to_page, name='back_to_page'),
    path('download/<uuid:post_id>/', views.download_file, name='download_file'),
]