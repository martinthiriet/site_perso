from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_encrypt, name="home_encrypt"),
    path("source/",views.source_code,name="source_code")
]