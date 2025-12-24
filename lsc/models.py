from django.db import models
import os 
from django.contrib.auth.models import User
import unicodedata
import numpy as np
from django.conf import settings

# lsc/models.py

from django.db import models
import numpy as np

class Camdata(models.Model):
    title = models.CharField(max_length=200, default="Untitled")
    data = models.TextField(default=r'<#a>1<a#><#t>Title<t#><#d>Description<d#><#id><id#>')
    unit = models.TextField(max_length=20,default='€')
    sources = models.TextField(default='')

    def save(self, *args, **kwargs):
        super(Camdata, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
