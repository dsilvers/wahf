import json
import uuid
from datetime import datetime

import stripe
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from membership.models import (
    MembershipEmailTemplateSnippet,
    MembershipLevel,
    MembershipRegistration,
)
from membership.utils import get_stripe_secret_key
from users.models import Member, User
from users.utils import send_email, usps_validate_user_address

stripe.api_key = get_stripe_secret_key()


@csrf_exempt
def process_stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse("Not POST", status=400)

    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError:
        return HttpResponse(status=400)

    if event.type == "customer.subscription.updated":
        process_subscription_update(event.data.object)
    # elif event.type in [
    #    "invoice.payment_failed",
    #    "invoice.payment_action_required",
    # ]:
    elif event.type == "customer.subscription.deleted":
        process_subscription_ending(event.data.object)

    return HttpResponse(status=200)


def process_subscription_ending(obj):
    member = Member.objects.filter(stripe_subscription_id=obj["id"])

    snippet = MembershipEmailTemplateSnippet.objects.get(slug="membership_expired")

    send_email(
        to=member.email,
        subject=snippet.subject,
        body=snippet.body,
        context={
            "member": member,
        },
    )


def process_subscription_update(obj):
    # Create User
    # USPS validate their address
    # Set their password
    # Send an email
    # Handle automatic payments (disable if not checked)
    # Delete Registration Data

    try:
        signup_uuid = obj["metadata"]["signup_uuid"]
    except Exception:
        signup_uuid = None

    # New registration?
    if signup_uuid:
        try:
            reg = MembershipRegistration.objects.get(id=signup_uuid)
        except MembershipRegistration.DoesNotExist:
            return

        user_data = reg.data["user"]

        if User.objects.filter(email=user_data["email"]).exists():
            raise Exception("Email address already exists")

        if not obj["plan"]["active"]:
            raise Exception("Subscription does not appear to be active.")

        start_date = datetime.utcfromtimestamp(obj["current_period_start"]).date()
        end_date = datetime.utcfromtimestamp(obj["current_period_end"]).date()

        user = User.objects.create_user(
            email=user_data["email"],
            password=str(uuid.uuid4()),  # this will get replaced with the hash later
        )
        user.password = reg.data["password_hash"]
        user.save()

        member = Member.objects.create(
            **{
                "user": user,
                "email": user_data["email"],
                "membership_level": MembershipLevel.objects.get(
                    id=reg.data["membership_level"]
                ),
                "membership_join_date": timezone.now().date(),
                "last_payment_date": start_date,
                "membership_expiry_date": end_date,
                "membership_automatic_payment": reg.data.get(
                    "automatic_payments_enabled", False
                ),
                "stripe_customer_id": obj["customer"],
                "stripe_subscription_id": obj["id"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "business_name": user_data["business_name"],
                "spouse_name": user_data["spouse_name"],
                "address_line1": user_data["address_line1"],
                "address_line2": user_data["address_line2"],
                "city": user_data["city"],
                "state": user_data["state"],
                "zip": user_data["zip"],
                "phone": user_data["phone"],
            }
        )

        # Attempt to validate the address
        member = usps_validate_user_address(member)

        # Handle automatic payments (disable subscription if they didn't want autopay)
        if not member.membership_automatic_payment:
            stripe.Subscription.modify(
                member.stripe_subscription_id, cancel_at_period_end=True
            )

        member.update_wahf_group_membership()
        reg.delete()

        # Send a renewal email
        snippet = MembershipEmailTemplateSnippet.objects.get(slug="join_thanks")

        send_email(
            to=member.email,
            subject=snippet.subject,
            body=snippet.body,
            context={
                "member": member,
            },
        )

        # Send a membership alert
        alert_body = render_to_string(
            "emails/membership_alert_signup.html", {"member": member}
        )

        send_email(
            to=["membership@wahf.org", "dan@wahf.org"],
            subject=f"WAHF Membership Signup - {member}",
            body=None,
            body_html=alert_body,
            context={
                "member": member,
            },
        )

        return

    # Renewal registration
    else:
        try:
            member = Member.objects.get(stripe_customer_id=obj["customer"])
        except Member.DoesNotExist:
            return

        old_subscription_id = member.stripe_subscription_id

        if not obj["plan"]["active"]:
            raise Exception("Subscription does not appear to be active.")

        start_date = datetime.utcfromtimestamp(obj["current_period_start"]).date()
        end_date = datetime.utcfromtimestamp(obj["current_period_end"]).date()

        member.last_payment_date = start_date
        member.membership_expiry_date = end_date
        member.stripe_subscription_id = obj["id"]
        member.save()

        # Cancel old subscription
        if old_subscription_id:
            try:
                stripe.Subscription.delete(old_subscription_id)
            except Exception:
                pass

        member.update_wahf_group_membership()

        # Send a renewal email
        snippet = MembershipEmailTemplateSnippet.objects.get(slug="renewal_thanks")

        send_email(
            to=member.email,
            subject=snippet.subject,
            body=snippet.body,
            context={
                "member": member,
            },
        )

        return
