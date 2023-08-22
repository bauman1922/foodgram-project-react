from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "password", "email", "name", "surname")
    search_fields = ("username",)
    list_filter = ("email", "username")
    empty_value_diplay = "-пусто-"


admin.site.register(User, UserAdmin)
