import json
from datetime import datetime

import stripe
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from membership.models import MembershipEmailTemplateSnippet, MembershipLevel
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

    if event.type == "checkout.session.completed":
        process_checkout_session_completed(event.data.object)

    # if event.type == "customer.subscription.updated":
    #    process_subscription_update(event.data.object)
    # elif event.type in [
    #    "invoice.payment_failed",
    #    "invoice.payment_action_required",
    # ]:
    # elif event.type == "customer.subscription.deleted":
    #    process_subscription_ending(event.data.object)

    return HttpResponse(status=200)


def process_checkout_session_completed(obj):
    session = stripe.checkout.Session.retrieve(
        obj["id"],
        expand=["line_items", "subscription"],
    )

    if session.metadata.get("action") != "signup":
        # Other actions here?
        return

    #################################
    # Process signup
    email = obj["customer_details"]["email"].lower()

    if User.objects.filter(email__iexact=email).exists():
        alert_body = render_to_string(
            "emails/membership_alert_duplicate_email.html", {"email": email}
        )

        send_email(
            to=["membership@wahf.org", "dan@wahf.org"],
            subject=f"WAHF Membership Error - Account Already Exists for {email}",
            body=None,
            body_html=alert_body,
            context={
                "email": email,
            },
        )

        raise Exception("Email address already exists")

    # Line item lookup for membership level
    try:
        membership_level = MembershipLevel.objects.get(
            stripe_price_id=session["line_items"]["data"][0]["price"]["id"]
        )
    except MembershipLevel.DoesNotExist:
        raise Exception("Membership level does not exist")

    if session["subscription"]:
        start_date = datetime.utcfromtimestamp(
            session["subscription"]["current_period_start"]
        ).date()
        end_date = datetime.utcfromtimestamp(
            session["subscription"]["current_period_end"]
        ).date()
    else:  # lifetime?
        start_date = timezone.now().date()
        end_date = None

    password = User.objects.make_random_password(length=8)
    user = User.objects.create_user(
        email=email,
        password=password,
    )

    name_split = session["shipping_details"]["name"].split(" ", 1)
    first_name = name_split[0]
    last_name = ""
    if len(name_split) == 2:
        last_name = name_split[1]

    line2 = session["shipping_details"]["address"]["line2"]

    subscription_id = session["subscription"]["id"] if session["subscription"] else ""

    member = Member.objects.create(
        **{
            "user": user,
            "email": email,
            "membership_level": membership_level,
            "membership_join_date": timezone.now().date(),
            "last_payment_date": start_date,
            "membership_expiry_date": end_date,
            "stripe_customer_id": session["customer"] or "",
            "stripe_subscription_id": subscription_id,
            "first_name": first_name,
            "last_name": last_name,
            "business_name": "",
            "spouse_name": "",
            "address_line1": session["shipping_details"]["address"]["line1"],
            "address_line2": line2 if line2 else "",
            "city": session["shipping_details"]["address"]["city"],
            "state": session["shipping_details"]["address"]["state"],
            "zip": session["shipping_details"]["address"]["postal_code"],
            "phone": "",
        }
    )

    # Validate member address
    # Update membership permissions
    # Send welcome email
    member = usps_validate_user_address(member)

    member.update_wahf_group_membership()

    snippet = MembershipEmailTemplateSnippet.objects.get(slug="join_thanks")

    snippet_body = snippet.body.replace("%EMAIL%", member.email)
    snippet_body = snippet_body.replace("%PASSWORD%", password)

    send_email(
        to=member.email,
        subject=snippet.subject,
        body=snippet_body,
        context={
            "member": member,
        },
    )

    # Send a membership alert to ourselves
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


"""
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
"""
