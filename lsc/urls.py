from django.urls import path
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('camplot/', views.camplot, name='camplot'),
    path('camlist/', views.camlist, name='camlist'),
    path('sources/', views.sources, name='sources'),
]