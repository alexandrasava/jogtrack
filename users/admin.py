from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    exclude = ('groups',)


admin.site.register(User, UserAdmin)
