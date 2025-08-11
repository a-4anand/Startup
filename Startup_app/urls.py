from django.contrib import admin
from django.urls import path,include

from Startup_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('form/', views.form_view, name='form'),
    path('resume-analyzer/', views.resume_analyzer, name='resume_analyzer'),
    path('download-resume-pdf/', views.download_resume_pdf, name='download_resume_pdf'),
]
