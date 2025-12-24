from django.shortcuts import render
from django.conf import settings


def home(request):
    return render(request, 'home.html', {'MEDIA_URL': settings.MEDIA_URL})

def musique(request):
    return render(request, 'musique_home.html', {'MEDIA_URL': settings.MEDIA_URL})