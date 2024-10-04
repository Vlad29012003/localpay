from django.contrib import admin
from .models import UserManager , User_mon , Pays , Comment

# Register your models here.


admin.site.register(User_mon)
admin.site.register(Pays)
admin.site.register(Comment)