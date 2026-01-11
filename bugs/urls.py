from django.urls import path
from . import views

app_name = 'bugs'  # This allows you to use 'bugs:report_bug' in templates

urlpatterns = [
    path('report/', views.report_bug, name='report_bug'),
    path('success/', views.report_success, name='report_success'),
]