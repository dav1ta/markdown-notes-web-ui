from django.contrib import admin
from .models import SubTags,Tags,UserSetting
# Register your models here.
admin.site.register(SubTags)
admin.site.register(Tags)
admin.site.register(UserSetting)
