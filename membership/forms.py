from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError

from membership.models import MembershipLevel
from users.models import Member


class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "email",
            "first_name",
            "last_name",
            "spouse_name",
            "business_name",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "zip",
            "phone",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False


class MemberJoinForm(forms.Form):
    membership_level = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    def clean(self):
        # Membership level should exist
        membership_level_lookup = self.cleaned_data.get("membership_level", None)
        membership_level = None

        if membership_level_lookup:
            membership_level = MembershipLevel.objects.filter(
                slug=membership_level_lookup
            ).first()
        if not membership_level:
            raise ValidationError("Please select a membership level above.")

        self.membership_level = membership_level

        return self.cleaned_data
