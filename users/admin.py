from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class WAHFUserAdmin(UserAdmin):
    model = User
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "last_login",
    )
    exclude = ("username",)
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )


admin.site.register(User, WAHFUserAdmin)
