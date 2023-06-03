from django.urls import path
from .import views

app_name='core'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),

    path('settings/', views.settings, name='settings'),
    path('uploadpost/', views.uploadpost, name='uploadpost'),
    path('likepost/', views.likePost, name='likepost'),
]