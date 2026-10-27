from django.urls import path
from . import views

urlpatterns = [
    path('organizations/<int:organization_id>/projects/', views.projects)
]