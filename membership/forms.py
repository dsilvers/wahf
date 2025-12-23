from django import forms


class MembershipSignupForm(forms.Form):
    level = forms.CharField(required=True)
    is_recurring = forms.BooleanField(required=False)

    # slug:amount,slug:amount
    additional_contributions = forms.CharField()

    total_amount = forms.FloatField(required=True)

    email = forms.EmailField(required=True)

    name = forms.CharField(required=True)
    spouse_name = forms.CharField(required=False)
    business_name = forms.CharField(required=False)

    phone = forms.CharField(required=True)

    line1 = forms.CharField(required=True)
    line2 = forms.CharField(required=False)
    city = forms.CharField(required=True)
    state = forms.CharField(required=True)
    zip = forms.CharField(required=True)
