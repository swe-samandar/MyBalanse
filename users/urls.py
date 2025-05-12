from django.urls import path
from .views import (
    SignUpView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    ResetPasswordRequestView,
    VerifyCodeView,
    SetNewPasswordView,
)

app_name = 'users'

urlpatterns = [
    path('register', SignUpView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password', ResetPasswordRequestView.as_view(), name='reset_password'),
    path('virefy-code', VerifyCodeView.as_view(), name='verify_code'),
    path('set-new-password', SetNewPasswordView.as_view(), name='set_new_password'),
]