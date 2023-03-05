from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class MemberProfileView(LoginRequiredMixin, TemplateView):
    template_name = "registration/member_profile.html"
