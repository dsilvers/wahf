import stripe
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.edit import FormView
from sentry_sdk import capture_exception

from membership.forms import MemberJoinForm, MemberUpdateForm
from membership.models import (
    MembershipJoinSnippet,
    MembershipRenewThanksSnippet,
    MembershipThanksSnippet,
)
from membership.utils import get_stripe_secret_key
from users.models import Member, User

stripe.api_key = get_stripe_secret_key()


class MemberProfileView(LoginRequiredMixin, TemplateView):
    template_name = "membership/member_profile.html"

    def get_context_data(self, **kwargs):
        self.request.session["renewal"] = False
        return super().get_context_data(**kwargs)


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


class MemberRenewPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # if not self.request.user.member
        # not self.request.user.member.membership_level
        # not self.request.user.member.membership_level.stripe_price_id
        # not self.request.user.member.stripe_customer_id

        payment_mode = "payment"
        if self.request.user.member.membership_level.allow_recurring_payments:
            payment_mode = "subscription"

        # Disallow renewing active subscriptions
        if self.request.user.member.stripe_subscription_active:
            return HttpResponseRedirect("/account/member-profile/")

        custom_fields = []

        if self.request.user.member.membership_level.includes_spouse:
            custom_fields.append(
                {
                    "key": "spousename",
                    "label": {"type": "custom", "custom": "Spouse Name"},
                    "type": "text",
                }
            )

        if self.request.user.member.membership_level.is_business:
            custom_fields.append(
                {
                    "key": "businessname",
                    "label": {"type": "custom", "custom": "Business Name"},
                    "type": "text",
                }
            )

        create_kwargs = {
            "line_items": [
                {
                    "price": self.request.user.member.membership_level.stripe_price_id,
                    "quantity": 1,
                },
            ],
            "mode": payment_mode,
            "success_url": "https://www.wahf.org/account/member-profile/",
            "cancel_url": "https://www.wahf.org/account/member-profile/",
            "billing_address_collection": "auto",
            "shipping_address_collection": {
                "allowed_countries": ["US"],
            },
            "allow_promotion_codes": True,
            "phone_number_collection": {
                "enabled": True,
            },
            "metadata": {"action": "renewal", "member_pk": self.request.user.member.pk},
            "custom_fields": custom_fields,
        }

        if self.request.user.member.stripe_customer_id:
            create_kwargs["customer"] = self.request.user.member.stripe_customer_id
        elif self.request.user.member.email:
            create_kwargs["customer_email"] = self.request.user.member.email

        if (
            self.request.user.member.membership_expiry_date
            and self.request.user.member.membership_expiry_date > timezone.now().date()
        ):
            create_kwargs["subscription_data"] = {
                "billing_cycle_anchor": int(
                    self.request.user.member.membership_expiry_date.strftime("%s")
                )
                + (60 * 60 * 24),
                "proration_behavior": "none",
            }

        try:
            checkout_session = stripe.checkout.Session.create(**create_kwargs)
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


class MemberRenewPublicPaymentView(View):
    # Use UUID to look up the user
    # Used by email invite
    def get(self, *args, **kwargs):
        try:
            member = Member.objects.get(uuid=self.kwargs["uuid"])
        except Member.DoesNotExist:
            return HttpResponseRedirect("/account/member-profile/")

        payment_mode = "subscription"
        if not member.membership_level.allow_recurring_payments:
            return HttpResponseRedirect("/account/member-profile/")

        # Disallow renewing active subscriptions
        if member.stripe_subscription_active:
            return HttpResponseRedirect("/account/member-profile/")

        custom_fields = []

        if member.membership_level.includes_spouse:
            custom_fields.append(
                {
                    "key": "spousename",
                    "label": {"type": "custom", "custom": "Spouse Name"},
                    "type": "text",
                }
            )

        if member.membership_level.is_business:
            custom_fields.append(
                {
                    "key": "businessname",
                    "label": {"type": "custom", "custom": "Business Name"},
                    "type": "text",
                }
            )

        create_kwargs = {
            "line_items": [
                {
                    "price": member.membership_level.stripe_price_id,
                    "quantity": 1,
                },
            ],
            "mode": payment_mode,
            "success_url": "https://www.wahf.org/renew/thanks/",
            "cancel_url": "https://www.wahf.org/account/member-profile/",
            "billing_address_collection": "auto",
            "shipping_address_collection": {
                "allowed_countries": ["US"],
            },
            "allow_promotion_codes": True,
            "phone_number_collection": {
                "enabled": True,
            },
            "metadata": {"action": "renewal", "member_pk": member.pk},
            "custom_fields": custom_fields,
        }

        if member.stripe_customer_id:
            create_kwargs["customer"] = member.stripe_customer_id
        elif member.email:
            create_kwargs["customer_email"] = member.email

        if (
            member.membership_expiry_date
            and member.membership_expiry_date > timezone.now().date()
        ):
            create_kwargs["subscription_data"] = {
                "billing_cycle_anchor": int(
                    member.membership_expiry_date.strftime("%s")
                )
                + (60 * 60 * 30),  # cheat for timezone conversion
                "proration_behavior": "none",
            }

        try:
            checkout_session = stripe.checkout.Session.create(**create_kwargs)
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

        custom_fields = []

        if form.membership_level.includes_spouse:
            custom_fields.append(
                {
                    "key": "spousename",
                    "label": {"type": "custom", "custom": "Spouse Name"},
                    "type": "text",
                }
            )

        if form.membership_level.is_business:
            custom_fields.append(
                {
                    "key": "businessname",
                    "label": {"type": "custom", "custom": "Business Name"},
                    "type": "text",
                }
            )

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
                phone_number_collection={
                    "enabled": True,
                },
                metadata={"action": "signup"},
                custom_fields=custom_fields,
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


class MemberRenewThanks(TemplateView):
    template_name = "membership/member_join_thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["snippet"] = MembershipRenewThanksSnippet.objects.first()
        return context


class RenewRedirect(RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        # Tag their session that they are trying to renew
        self.request.session["renewal"] = True

        return "/accounts/login/?next=/account/member-profile/"


class KohnDonateRedirect(View):
    permanent = False
    query_string = False

    def get(self, *args, **kwargs):
        price_lookup = kwargs.get("price", None)

        default = "price_1Onlr2Kymtko2mUA2q57jpdj"
        price_map = {
            25: "price_1OnlnMKymtko2mUApH9ZdiFo",
            50: "price_1OnlnyKymtko2mUAo1jFujQe",
            100: "price_1OnloCKymtko2mUAl5ZMxbJA",
            250: "price_1OnloaKymtko2mUAG0WdzoaS",
            500: "price_1OnloaKymtko2mUAG0WdzoaS",
            750: "price_1OnlomKymtko2mUA2v01z29T",
            1000: "price_1OnloxKymtko2mUAjkoqIIfK",
            2000: "price_1OnlpBKymtko2mUABLvJDPWo",
            3000: "price_1OnlpnKymtko2mUALZ3y0Vyx",
            5000: "price_1Onlq3Kymtko2mUA7UlYVMFR",
            7500: "price_1OnlqDKymtko2mUA2U3wPKs0",
            10000: "price_1OnlqOKymtko2mUAforXj1PX",
        }

        price_id = price_map.get(price_lookup, default)

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url="https://www.wahf.org/kohn/thanks",
                cancel_url="https://www.wahf.org/kohn/",
                billing_address_collection="auto",
                allow_promotion_codes=False,
                metadata={"action": "kohn"},
            )
        except Exception as e:
            # if hasattr(e, "user_message"):
            #    # self.request.session["payment_error"] = e.user_message
            if settings.SENTRY_DSN:
                capture_exception(e)
            return HttpResponseRedirect(reverse("kohn"))

        response = HttpResponse(content="", status=303)
        response["Location"] = checkout_session.url
        return response
