import json

import stripe
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView, View
from sentry_sdk import capture_exception

from membership.forms import MembershipSignupForm
from membership.models import (
    Member,
    MembershipContributionType,
    MembershipLevel,
    MembershipThanksSnippet,
)
from membership.utils import get_stripe_secret_key
from users.models import User

stripe.api_key = get_stripe_secret_key()


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
            "allow_promotion_codes": True,
            "phone_number_collection": {
                "enabled": True,
            },
            "metadata": {"action": "renewal", "member_pk": member.pk},
            "custom_fields": custom_fields,
            "automatic_tax": {"enabled": False},
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


class MemberJoinView(View):
    def get(self, request):
        context = {}
        context["membership_levels"] = MembershipLevel.objects.filter(
            show_on_membership_page=True
        ).order_by("membership_page_sequence")
        context["contribution_types"] = MembershipContributionType.objects.all()

        membership_json = {}
        for level in context["membership_levels"]:
            membership_json[level.slug] = {
                "id": level.pk,
                "name": level.name,
                "slug": level.slug,
                "price": level.price,
                "price_display": level.price_display,
                "allow_recurring": level.allow_recurring_payments,
                "icon": level.membership_page_icon,
                "includes_spouse": level.includes_spouse,
                "is_business": level.is_business,
            }
        context["membershipLevelJSON"] = json.dumps(membership_json)

        return render(request, "membership/member_join.html", context)

    def post(self, request):
        # member level
        # additional contribution amounts
        # total amount
        # email
        # name
        # spouse / biz name
        # address1, address2, city, state, zip
        # is recurring
        form = MembershipSignupForm(request.POST)

        if not form.is_valid():
            return JsonResponse({"error": "invalid form"})

        try:
            level = MembershipLevel.objects.get(slug=form.cleaned_data["level"])
        except MembershipLevel.DoesNotExist:
            return JsonResponse({"error": "invalid level"})

        kwargs = {
            "ui_mode": "embedded",
            "shipping_address_collection": {
                "allowed_countries": ["US"],
            },
            "metadata": {},
            "line_items": [],
            "allow_promotion_codes": True,
            "phone_number_collection": {"enabled": True},
            "return_url": "https://www.wahf.org/membership/thanks",
        }

        # Recurring payment
        if level.allow_recurring_payments and form.cleaned_data["is_recurring"]:
            is_recurring = True
            kwargs["mode"] = "subscription"
            kwargs["payment_method_collection"] = "always"
            stripe_payment_id = level.stripe_price_id
        else:
            is_recurring = False
            kwargs["mode"] = "payment"
            stripe_payment_id = level.stripe_price_id_one_time

        if not stripe_payment_id:
            raise Exception(
                f"Missing stripe payment id for {level}, recurring: {is_recurring}"
            )

        # Can use a biz name or spouse
        if level.includes_spouse:
            kwargs["metadata"]["spouse"] = form.cleaned_data["spouse_name"]
        if level.is_business:
            kwargs["metadata"]["business"] = form.cleaned_data["business_name"]

        # Signup signal
        kwargs["metadata"]["action"] = "signup"

        # Add primary item first
        kwargs["line_items"].append(
            {
                "price": stripe_payment_id,
                "quantity": 1,
            }
        )

        # Add any addon contributions
        additional = form.cleaned_data["additional_contributions"]
        if additional:
            for addon in additional.split(","):
                try:
                    slug, amount_str = addon.split(":")
                    amount = float(amount_str)
                except ValueError:
                    return JsonResponse({"error": "invalid addon"})

                try:
                    addon_type_obj = MembershipContributionType.objects.get(slug=slug)
                except MembershipContributionType.DoesNotExist:
                    return JsonResponse({"error": "missing addon"})

                if amount > 0.0:
                    addon_data = {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(amount * 100),
                            "product_data": {
                                "name": addon_type_obj.name,
                                "description": addon_type_obj.description,
                            },
                        },
                        "quantity": 1,
                    }

                    if is_recurring:
                        addon_data["price_data"]["recurring"] = {"interval": "year"}

                    kwargs["line_items"].append(addon_data)

        # Create or update a subscription
        try:
            existing_customers = stripe.Customer.list(
                email=form.cleaned_data["email"], limit=1
            ).data
            if existing_customers:
                customer = existing_customers[0]
            else:
                address_data = {
                    "line1": form.cleaned_data["line1"],
                    "line2": form.cleaned_data["line2"],
                    "city": form.cleaned_data["city"],
                    "state": form.cleaned_data["state"],
                    "postal_code": form.cleaned_data["zip"],
                    "country": "US",
                }

                customer = stripe.Customer.create(
                    email=form.cleaned_data["email"],
                    name=form.cleaned_data["name"],
                    phone=f"+1{form.cleaned_data['phone']}",
                    address=address_data,
                    shipping={
                        "name": form.cleaned_data["name"],
                        "address": address_data,
                    },
                )

            kwargs["customer"] = customer.id

            checkout_session = stripe.checkout.Session.create(**kwargs)

        except Exception as e:
            if settings.SENTRY_DSN:
                capture_exception(e)
            print(e)

            return JsonResponse({"error": "stripe error"})

        return JsonResponse({"checkoutSession": checkout_session.client_secret})


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
