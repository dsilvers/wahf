from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import MemberJoinForm


class MemberProfileView(LoginRequiredMixin, TemplateView):
    template_name = "registration/member_profile.html"


class MemberJoinView(FormView):
    template_name = "registration/member_join.html"
    form_class = MemberJoinForm
    success_url = "/membership/thanks"
