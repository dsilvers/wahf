from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Member

User = get_user_model()


# class WAHFMemberAdmin(admin.ModelAdmin):
#    model = Member
#    ordering = ("last_name", "first_name")
#    search_fields = ("first_name", "last_name")
#    list_display = (
#        "first_name",
#        "last_name",
#        "membership_level",
#    )


class WAHFMemberAdminInline(admin.StackedInline):
    model = Member


class WAHFUserAdmin(admin.ModelAdmin):
    model = User
    ordering = ("last_name", "first_name")
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
        (None, {"fields": ("email", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )
    inlines = [WAHFMemberAdminInline]


# admin.site.register(Member, WAHFMemberAdmin)
admin.site.register(User, WAHFUserAdmin)
