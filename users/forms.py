from crispy_forms.helper import FormHelper
from django import forms
from localflavor.us.forms import USStateSelect


class MemberJoinForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput())

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

    membership_level = forms.TextInput()
    membership_automatic_payments = forms.BooleanField(
        label="Automatically Renew My Membership",
        help_text="In late December, we can attempt to automatically renew your membership for the upcoming year. You can disable this anytime in the your payment profile or by contacting us.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
