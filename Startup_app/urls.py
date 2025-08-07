from django.contrib import admin
from django.urls import path,include

from Startup_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('form/', views.form_view, name='form'),
    path('analyze_resume/', views.analyze_resume, name='analyze_resume'),
    path('ask_gemini/', views.ask_gemini, name='ask_gemini'),
    path('resume/', views.resume_analyzer, name='resume_analyzer')
]
