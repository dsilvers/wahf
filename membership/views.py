import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from sentry_sdk import capture_exception

from membership.forms import MemberJoinForm, MemberJoinPaymentForm, MemberUpdateForm
from membership.models import MembershipJoinSnippet, MembershipThanksSnippet
from membership.utils import get_stripe_secret_key
from users.models import Member, User

stripe.api_key = get_stripe_secret_key()


class MemberProfileView(LoginRequiredMixin, TemplateView):
    template_name = "membership/member_profile.html"


class MemberUpdateFormView(LoginRequiredMixin, FormView):
    template_name = "membership/member_update.html"
    form_class = MemberUpdateForm
    success_url = "/account/member-profile/"

    def get_form(self):
        try:
            member = Member.objects.get(user=self.request.user)
            return self.form_class(instance=member, **self.get_form_kwargs())
        except Member.RelatedObjectDoesNotExist:
            return self.form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class MemberRenewPaymentView(LoginRequiredMixin, FormView):
    template_name = "membership/member_renew_payment.html"
    form_class = MemberJoinPaymentForm

    # def get_form_kwargs(self):
    #    kwargs = super().get_form_kwargs()
    #    kwargs.update({'membership_automatic_payments_trigger': self.request.user.member.membership_automatic_payment})
    #    return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        member = self.request.user.member

        days_remaining = 0
        if member.membership_expiry_date:
            days_remaining = (
                member.membership_expiry_date - timezone.now().date()
            ).days
            if days_remaining < 0:
                days_remaining = 0

        payment_error = self.request.session.get("payment_error")
        if payment_error:
            context["payment_error"] = payment_error
            del self.request.session["payment_error"]

        context["member"] = member

        # Update member details at Stripe
        customer_name = f"{member.first_name} {member.last_name}"
        if member.business_name:
            customer_name = f"{customer_name} ({member.business_name})"
        elif member.spouse_name:
            customer_name = f"{customer_name} + {member.spouse_name}"

        stripe_customer_args = {
            "email": member.email,
            "name": customer_name,
            "shipping": {
                "address": {
                    "city": member.city,
                    "country": "US",
                    "line1": member.address_line1,
                    "line2": member.address_line2,
                    "postal_code": member.zip,
                    "state": member.state,
                },
                "name": customer_name,
            },
            "address": {
                "city": member.city,
                "country": "US",
                "line1": member.address_line1,
                "line2": member.address_line2 if member.address_line2 else "",
                "postal_code": member.zip,
                "state": member.state,
            },
        }

        try:
            stripe.Customer.modify(
                self.member.stripe_customer_id, **stripe_customer_args
            )
        except Exception as e:
            if hasattr(e, "user_message"):
                self.request.session["payment_error"] = e.user_message
            else:
                if settings.SENTRY_DSN:
                    capture_exception(e)
                print(e)
                self.request.session[
                    "payment_error"
                ] = "An error occurred, give it a try again. If it continues to occur, please contact us."

        # Create new subscription
        trial_period_days = 0
        if member.membership_expiry_date > timezone.now().date():
            trial_period_days = (
                member.membership_expiry_date - timezone.now().date()
            ).days

        try:
            subscription_response = stripe.Subscription.create(
                customer=member.stripe_customer_id,
                items=[
                    {
                        "price": member.membership_level.stripe_price_id,
                    }
                ],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                trial_period_days=trial_period_days,
            )
        except Exception as e:
            if hasattr(e, "user_message"):
                self.request.session["payment_error"] = e.user_message
            else:
                if settings.SENTRY_DSN:
                    capture_exception(e)
                print(e)
                self.request.session[
                    "payment_error"
                ] = "An error occurred, give it a try again. If it continues to occur, please contact us."
        else:
            context[
                "subscription_client_secret"
            ] = subscription_response.latest_invoice.payment_intent.client_secret

        context["membership_level"] = self.request.user.member.membership_level
        context["snippet"] = MembershipJoinSnippet.objects.first()

        return context

    def form_valid(self, form):
        # Cancel current subscription if one is active
        # Create a new subscription with the remaining number of days in their period as a trial period

        autopay = (
            True if form.cleaned_data.get("membership_automatic_payments") else False
        )

        self.get_context_data()

        self.reg.data["automatic_payments_enabled"] = autopay
        self.reg.save()

        try:
            del self.request.session["registration_uuid"]
        except Exception:
            pass

        return HttpResponseRedirect(reverse("member_profile"))


class MemberJoinView(FormView):
    template_name = "membership/member_join.html"
    form_class = MemberJoinForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        payment_error = self.request.session.get("payment_error")
        if payment_error:
            context["payment_error"] = payment_error
            del self.request.session["payment_error"]

        context["snippet"] = MembershipJoinSnippet.objects.first()

        return context

    def form_valid(self, form):
        if not form.membership_level:
            self.request.session[
                "payment_error"
            ] = "Please select a membership level above."
            return HttpResponseRedirect(reverse("membership-join"))

        if not form.membership_level.stripe_price_id:
            self.request.session[
                "payment_error"
            ] = "Problem creating subscription, this method does not a price ID set."
            return HttpResponseRedirect(reverse("membership-join"))

        payment_mode = "payment"
        if form.membership_level.allow_recurring_payments:
            payment_mode = "subscription"

        # Create or update a subscription
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price": form.membership_level.stripe_price_id,
                        "quantity": 1,
                    },
                ],
                mode=payment_mode,
                success_url="https://www.wahf.org/membership/thanks/",
                cancel_url="https://www.wahf.org/membership/",
                billing_address_collection="auto",
                shipping_address_collection={
                    "allowed_countries": ["US"],
                },
                allow_promotion_codes=True,
                metadata={"action": "signup"},
            )

        except Exception as e:
            if hasattr(e, "user_message"):
                self.request.session["payment_error"] = e.user_message
            else:
                if settings.SENTRY_DSN:
                    capture_exception(e)
                print(e)
                self.request.session[
                    "payment_error"
                ] = "An error occurred, give it a try again. If it continues to occur, please contact us."
            return HttpResponseRedirect(reverse("membership-join"))

        response = HttpResponse(content="", status=303)
        response["Location"] = checkout_session.url
        return response


class MemberJoinThanks(TemplateView):
    template_name = "membership/member_join_thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "reg_login" in self.request.session:
            # check if member exists, if it does, do the login
            user = User.objects.filter(email=self.request.session["reg_login"]).first()
            print("user", user)
            if user:
                del self.request.session["reg_login"]
                login(self.request, user)
                print("logged in")
            else:
                context["do_refresh"] = True
                print("need the refresh")
        else:
            print("no reg login found")

        context["snippet"] = MembershipThanksSnippet.objects.first()
        return context
