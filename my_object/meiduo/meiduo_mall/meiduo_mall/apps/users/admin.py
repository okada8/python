from django.contrib import admin
from .models import User

# Register your models here.



class Userconfig(admin.ModelAdmin):
    list_display = ['id','username','email','email_active','is_staff']
    list_display_links =['id','username','email','email_active','is_staff']





admin.site.register(User,Userconfig)

