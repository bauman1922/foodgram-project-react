from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = ("username",)
    list_filter = ("email", "first_name",)
    empty_value_display = "-пусто-"


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "author",
    )
    search_fields = ("user", "author")
    list_filter = ("user", "author")
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
