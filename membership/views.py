import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from sentry_sdk import capture_exception

from membership.forms import MemberJoinForm, MemberJoinPaymentForm, MemberUpdateForm
from membership.models import (
    MembershipJoinSnippet,
    MembershipLevel,
    MembershipRegistration,
    MembershipThanksSnippet,
)
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
                "line2": member.address_line2,
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
        form_data = form.cleaned_data

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

        if User.objects.filter(email=form_data["email"]).exists():
            return HttpResponseRedirect(
                reverse("password_reset-join") + "?message=dupe"
            )

        # Get or create registration tracker
        reg_uuid = self.request.session.get("registration_uuid")
        reg = None
        if reg_uuid:
            reg = MembershipRegistration.objects.filter(id=reg_uuid).first()
        if not reg:
            reg = MembershipRegistration.objects.create()
            self.request.session["registration_uuid"] = str(reg.id)

        reg.data["membership_level"] = form.membership_level.id
        reg.data["password_hash"] = make_password(form_data["password"])
        reg.data["user"] = {
            "email": form_data["email"],
            "first_name": form_data["first_name"],
            "last_name": form_data["last_name"],
            "spouse_name": form_data["spouse_name"],
            "business_name": form_data["business_name"],
            "address_line1": form_data["address_line1"],
            "address_line2": form_data["address_line2"],
            "city": form_data["city"],
            "state": form_data["state"],
            "zip": form_data["zip"],
            "phone": form_data["phone"],
        }
        reg.save()

        customer_name = f"{form_data['first_name']} {form_data['last_name']}"
        if form_data["business_name"]:
            customer_name = f"{customer_name} ({form_data['business_name']})"
        elif form_data["spouse_name"]:
            customer_name = f"{customer_name} + {form_data['spouse_name']}"

        stripe_customer_args = {
            "email": form_data["email"],
            "name": customer_name,
            "shipping": {
                "address": {
                    "city": form_data["city"],
                    "country": "US",
                    "line1": form_data["address_line1"],
                    "line2": form_data["address_line2"],
                    "postal_code": form_data["zip"],
                    "state": form_data["state"],
                },
                "name": customer_name,
            },
            "address": {
                "city": form_data["city"],
                "country": "US",
                "line1": form_data["address_line1"],
                "line2": form_data["address_line2"],
                "postal_code": form_data["zip"],
                "state": form_data["state"],
            },
        }

        # Create the customer at Stripe
        # Save the customer ID between form submissions in the event the charge errors or something
        try:
            if reg.data.get("stripe_customer_id"):
                stripe.Customer.modify(
                    reg.data.get("stripe_customer_id"), **stripe_customer_args
                )
            else:
                # Create stripe customer
                create_customer_response = stripe.Customer.create(
                    **stripe_customer_args
                )
                reg.data["stripe_customer_id"] = create_customer_response.id
                reg.save()
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

        # Create or update a subscription
        try:
            if not reg.data.get("stripe_subscription_id"):
                subscription_response = stripe.Subscription.create(
                    customer=reg.data["stripe_customer_id"],
                    items=[
                        {
                            "price": form.membership_level.stripe_price_id,
                        }
                    ],
                    payment_behavior="default_incomplete",
                    payment_settings={"save_default_payment_method": "on_subscription"},
                    expand=["latest_invoice.payment_intent"],
                    metadata={
                        "signup_uuid": str(reg.id),
                    },
                )
                reg.data["stripe_subscription_id"] = subscription_response.id
                reg.data["stripe_subscription_item_id"] = subscription_response[
                    "items"
                ]["data"][0]["id"]
                reg.data[
                    "subscription_client_secret"
                ] = subscription_response.latest_invoice.payment_intent.client_secret
                reg.save()
            else:
                subscription_response = stripe.SubscriptionItem.modify(
                    reg.data["stripe_subscription_item_id"],
                    price=form.membership_level.stripe_price_id,
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

        return HttpResponseRedirect(reverse("membership-join-payment"))


class MemberJoinPaymentView(FormView):
    template_name = "membership/member_join_payment.html"
    form_class = MemberJoinPaymentForm

    def dispatch(self, request, *args, **kwargs):
        reg_uuid = self.request.session.get("registration_uuid")
        if not reg_uuid:
            return HttpResponseRedirect(reverse("membership-join"))

        self.reg = MembershipRegistration.objects.filter(id=reg_uuid).first()
        if not self.reg:
            return HttpResponseRedirect(reverse("membership-join"))

        self.membership_level = MembershipLevel.objects.filter(
            id=self.reg.data["membership_level"]
        ).first()
        if not self.membership_level:
            self.request.session["payment_error"] = "Membership level not found"
            return HttpResponseRedirect(reverse("membership-join"))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["subscription_client_secret"] = self.reg.data[
            "subscription_client_secret"
        ]
        context["membership_level"] = self.membership_level
        context["snippet"] = MembershipJoinSnippet.objects.first()

        return context

    def form_valid(self, form):
        autopay = (
            True if form.cleaned_data.get("membership_automatic_payments") else False
        )

        self.reg.data["automatic_payments_enabled"] = autopay
        self.reg.save()

        self.request.session["reg_login"] = self.reg.data["user"]["email"]

        try:
            del self.request.session["registration_uuid"]
        except Exception:
            pass

        return HttpResponseRedirect(reverse("membership-join-thanks"))


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
