from django.urls import path
from django.contrib.auth import views as auth_views
from .import views

# app_name='core'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),

    path('settings/', views.settings, name='settings'),
    path('uploadpost/', views.uploadpost, name='uploadpost'),
    path('likepost/', views.likePost, name='likepost'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('followunfollow/', views.followunfollow, name='followunfollow'),

    path('search/', views.search, name='search'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
]