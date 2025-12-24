from django.contrib import admin
from .models import Camdata

# Register your models here.

class CamdataAdmin(admin.ModelAdmin):
    list_display = ('title','id')  
    list_display_links = ('title','id')
    readonly_fields = ('id',)


admin.site.register(Camdata,CamdataAdmin)
