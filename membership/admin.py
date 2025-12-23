from django.contrib import admin

from membership.models import MembershipContributionType, MembershipLevel

admin.site.register(MembershipLevel)
admin.site.register(MembershipContributionType)
