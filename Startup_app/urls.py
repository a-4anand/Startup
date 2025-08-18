from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from Startup_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('form/', views.form_view, name='form'),
    path('resume-analyzer/', views.resume_analyzer, name='resume_analyzer'),
    path('download-resume-pdf/', views.download_resume_pdf, name='download_resume_pdf'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path("profile", views.profile_view, name='profile'),
    path('logout/', views.user_logout, name='logout'),
path('verify-otp/', views.otp_verify_view, name='otp_verify'),
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='Startup_app/password/password_reset.html'),
         name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='Startup_app/password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='Startup_app/password/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='Startup_app/password/password_reset_complete.html'),
         name='password_reset_complete'),


]
