from django.urls import path
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('getsong/', views.getsong, name='getsong'),
    path('pres_et/', views.pres_et, name='pres_et'),
]