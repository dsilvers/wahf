from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from localflavor.us.forms import USStateSelect

from membership.models import MembershipLevel
from users.models import Member, User


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
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Your password is used to access our magazine, Forward in Flight, access member content, and manage your member profile.",
    )

    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    business_name = forms.CharField(
        max_length=200, required=False, label="Business / Corporate Name"
    )
    spouse_name = forms.CharField(max_length=200, required=False)

    address_line1 = forms.CharField(max_length=200, label="Address - Line 1")
    address_line2 = forms.CharField(
        max_length=200, label="Address - Line 2", required=False
    )
    city = forms.CharField(max_length=200)
    state = forms.CharField(widget=USStateSelect(), initial="WI")
    zip = forms.CharField(max_length=200, label="Zip Code")

    phone = forms.CharField(max_length=200, required=False, label="Phone Number")

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

        # Check if the email address already exists
        email = self.cleaned_data.get("email", None)
        if not email or User.objects.filter(email=email).exists():
            raise ValidationError("EXISTING_USER")

        return self.cleaned_data


class MemberJoinPaymentForm(forms.Form):
    membership_automatic_payments_trigger = forms.BooleanField(
        label="Automatically Renew My Membership",
        required=False,
    )
    membership_automatic_payments = forms.BooleanField(
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
