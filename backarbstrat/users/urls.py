from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.userRegister, name='register'),
    path('verify/', views.verify, name='verify'),
    path('login/', views.login, name='login'),
    path('currentUser/', views.getCurrentUser, name='currentUser'),
    path('userUpdate/', views.userName_update, name='userUpdate'),
    path('emailUpdate/', views.userEmail_update, name='emailUpdate'),
    path('passUpdate/', views.userPass_update, name='passUpdate'),
    path('imageUpdate/', views.userImg_update, name='imageUpdate'),
    path('deleteUserImage/', views.deleteUserImage, name='deleteUserImage'),
    path('recoveryPassword/', views.recoveryPassword, name='recoveryPassword'),
]

