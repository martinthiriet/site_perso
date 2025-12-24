# your_app_name/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('musique/', views.musique, name='musique'),
]