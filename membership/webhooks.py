import json
from datetime import datetime

import pytz
import stripe
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from membership.models import (
    BanquetPayment,
    MembershipEmailTemplateSnippet,
    MembershipLevel,
)
from membership.utils import get_stripe_secret_key, send_membership_error_email
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
        session = stripe.checkout.Session.retrieve(
            event.data.object["id"],
            expand=["line_items", "subscription"],
        )

        action = session.metadata.get("action", None)

        if action == "signup":
            process_membership_signup(event.data.object, session)
        elif action == "renewal":
            # this is currently unused and does nothing
            process_membership_renewal(event.data.object, session)
        elif action == "donation":
            process_donation_payment(event.data.object, session)
        elif action == "banquet":
            process_banquet_tickets(event.data.object, session)

    elif event.type in [
        "customer.subscription.created",
        "customer.subscription.updated",
    ]:
        # Update the subscription dates and status
        # This one might fire before the subscription is there, so we can delay it and tell stripe to come back
        return process_subscription_create_update(event.data.object)

    elif event.type == "customer.subscription.deleted":
        # Update the status of the subscription
        process_subscription_delete(event.data.object)

    return HttpResponse(status=200)


def process_banquet_tickets(obj, session):
    #
    #
    # THE ENTRIES AT STRIPE NEED TO BE UPDATED FOR 2024
    #
    #
    #

    # Total amount paid
    amount_total = session["amount_total"] / 100.0

    # Name
    # Phone
    # Zip Code
    name = session["customer_details"]["name"]
    phone = session["customer_details"]["phone"].replace("+1", "")
    email = session["customer_details"]["email"]

    # Item they purchased
    item = session["line_items"]["data"][0]["description"]
    quantity = session["line_items"]["data"][0]["quantity"]

    stripe_id = session["id"]

    attendee_names = "(no names supplied at checkout)"
    docent_tour = "Was not selected during checkout"

    paid_date = datetime.utcfromtimestamp(session["created"]).replace(tzinfo=pytz.utc)

    item_type = "ticket"
    if "table" in item.lower():
        item_type = "table"

    if quantity > 1:
        item_type = f"{item_type}s"

    if "table" in item.lower():
        item_type = f"{item_type} of 8 attendees"

    for cf in session["custom_fields"]:
        if cf["key"] == "attendeenames":
            attendee_names = (
                cf["text"]["value"] if cf["text"]["value"] else attendee_names
            )
        elif cf["key"] == "eaamuseumdocentguidedtour":
            docent_tour = (
                "Yes, will attend the docent tour."
                if cf["dropdown"]["value"] and cf["dropdown"]["value"].startswith("no")
                else "No, we will not attend the docent tour."
            )

    confirmation_body = render_to_string(
        "emails/banquet_confirmation.html",
        {
            "amount_total": amount_total,
            "name": name,
            "email": email,
            "phone": phone,
            "item": item,
            "item_type": item_type,
            "quantity": quantity,
            "attendee_names": attendee_names,
            "docent_tour": docent_tour,
            "paid_date": paid_date,
            "stripe_id": stripe_id,
        },
    )

    send_email(
        to=[email, "president@wahf.org"],
        subject=f"WAHF 2023 Investiture Dinner and Ceremony - RSVP Confirmation - {name}",
        body=None,
        body_html=confirmation_body,
        context={
            "email": email,
        },
    )

    send_email(
        to=["dan@wahf.org", "rosedorceyFIF@gmail.com"],
        subject=f"WAHF 2023 Investiture Dinner and Ceremony - RSVP Confirmation - {name}",
        body=None,
        body_html=confirmation_body,
        context={
            "email": email,
        },
    )

    BanquetPayment.objects.create(
        stripe_id=stripe_id,
        amount_total=amount_total,
        name=name,
        email=email,
        phone=phone,
        item=item,
        quantity=quantity,
        attendee_names=attendee_names,
        docent_tour=docent_tour,
        signup_date=paid_date,
    )

    return


def process_donation_payment(obj, session):
    # Send them the donation receipt
    name = session["customer_details"]["name"]
    if name.lower() == name:
        name = name.title()

    line2 = session["customer_details"]["address"]["line2"] or ""
    line1 = session["customer_details"]["address"]["line1"]
    city = session["customer_details"]["address"]["city"]
    state = session["customer_details"]["address"]["state"]
    zip = session["customer_details"]["address"]["postal_code"]

    email = obj["customer_details"]["email"].lower()

    donation_amount = obj["amount_total"] / 100.0
    donation_amount_str = f"{donation_amount:.2f}"

    date_str = timezone.now().strftime("%B %-d, %Y")

    replacements = [
        ("%DATE%", date_str),
        ("%EMAIL%", email),
        ("%NAME%", name),
        ("%LINE1%", line1),
        ("%LINE2%", line2),
        ("%CITY%", city),
        ("%STATE%", state),
        ("%ZIP%", zip),
        ("%AMOUNT%", donation_amount_str),
    ]

    snippet = MembershipEmailTemplateSnippet.objects.get(slug="donation_thanks")
    snippet_body = snippet.body

    for replacement_key, replacement_value in replacements:
        snippet_body = snippet_body.replace(replacement_key, replacement_value)

    send_email(
        to=email,
        subject=snippet.subject,
        body=snippet_body,
        context={},
    )

    return


def process_membership_signup(obj, session):
    #################################
    # Process signup
    email = obj["customer_details"]["email"].lower()

    if User.objects.filter(email__iexact=email).exists():
        error = f"""
            Unable to create WAHF account or process signup for <b>{ email }</b>, as it already exists in our users database.
            <br><br>
            This membership probably needs to be manually processed and an account created for a different email address if necessary. Sorry!
        """

        send_membership_error_email(
            f"WAHF Membership Creation Error - Account Already Exists for {email}",
            error,
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

    phone = obj["customer_details"].get("phone")
    phone = phone.replace("+1", "") if phone else ""

    subscription_id = session["subscription"]["id"] if session["subscription"] else ""

    spouse_name = ""
    business_name = ""

    for field in obj.get("custom_fields", []):
        if field["key"] == "spousename":
            spouse_name = field["text"]["value"]
        elif field["key"] == "businessname":
            business_name = field["text"]["value"]

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
            "stripe_subscription_active": True,
            "first_name": first_name,
            "last_name": last_name,
            "business_name": business_name,
            "spouse_name": spouse_name,
            "address_line1": session["shipping_details"]["address"]["line1"],
            "address_line2": line2 if line2 else "",
            "city": session["shipping_details"]["address"]["city"],
            "state": session["shipping_details"]["address"]["state"],
            "zip": session["shipping_details"]["address"]["postal_code"],
            "phone": phone,
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


def process_membership_renewal(obj, session):
    return
    """
    # Expired renewals where the subscription is dead and needs to be recreated
    email = obj["customer_details"]["email"].lower()
    member_pk = session.metadata.get("member_pk", None)
    member = Member.objects.filter(pk=member_pk).first() if member_pk else None

    if not member_pk or not member:
        send_membership_error_email(
            f"WAHF Membership Renewal Error - Unable to find member #{member_pk}",
            f"A renewal was submitted for member with ID# {member_pk}, but we are not finding that ID in our WAHF database.",
        )
        raise Exception("Member PK not found")

    # Process renewal
    start_date = datetime.utcfromtimestamp(obj["current_period_start"]).date()
    end_date = datetime.utcfromtimestamp(obj["current_period_end"]).date()

    member.last_payment_date = start_date
    member.membership_expiry_date = end_date
    member.stripe_subscription_id = obj["id"]
    member.stripe_subscription_active = obj["status"] == "active"
    member.save()

    member.update_wahf_group_membership()

    # Send a membership alert to ourselves
    alert_body = render_to_string(
        "emails/membership_alert_signup.html", {"member": member, "renewal": True}
    )

    send_email(
        to=["membership@wahf.org", "dan@wahf.org"],
        subject=f"WAHF Membership Renewal - {member}",
        body=None,
        body_html=alert_body,
        context={
            "member": member,
        },
    )

    return
    """


def process_subscription_create_update(obj):
    subscription_id = obj["id"]

    member = Member.objects.filter(stripe_subscription_id=subscription_id).first()
    if not member:
        # possibly a new subscription for someone without an existing one?
        customer = stripe.Customer.retrieve(obj["customer"])
        email = customer["email"]

        member = Member.objects.filter(email__iexact=email).first()

        if not member:
            print(
                f"Unknown member from subscription ID {subscription_id} or email address"
            )
            return HttpResponse("Unknown Member")

        if member.stripe_customer_id and member.stripe_customer_id != obj["customer"]:
            # Customer is new and does not match, something weird happened
            print(
                f"Unknown customer created this subscription, one already exists with that email {email}"
            )
            return HttpResponse("Duplicate email account")

        member.stripe_customer_id = obj["customer"]
        member.stripe_subscription_id = subscription_id

    # Update dates on subscription
    previous_end_date = member.membership_expiry_date
    # previous_status = member.stripe_subscription_active

    start_date = datetime.utcfromtimestamp(obj["current_period_start"]).date()
    end_date = datetime.utcfromtimestamp(obj["current_period_end"]).date()

    member.last_payment_date = start_date
    member.membership_expiry_date = end_date
    member.stripe_subscription_active = obj["status"] == "active"
    member.save()

    member.update_wahf_group_membership()

    if end_date > previous_end_date and member.stripe_subscription_active:
        # Renewed?

        # Email member
        snippet = MembershipEmailTemplateSnippet.objects.get(
            slug="renew_thanks_automatic"
        )
        send_email(
            to=[member.email],
            subject=snippet.subject,
            body=snippet.body,
            context={
                "member": member,
            },
        )

        # Email administration
        alert_body = render_to_string(
            "emails/membership_alert_signup.html", {"member": member, "renewal": True}
        )
        send_email(
            to=["membership@wahf.org", "dan@wahf.org"],
            subject=f"WAHF Membership Auto Renewal - {member}",
            body=None,
            body_html=alert_body,
            context={
                "member": member,
            },
        )

    return HttpResponse("OK")


def process_subscription_delete(obj):
    subscription_id = obj["id"]

    member = Member.objects.filter(stripe_subscription_id=subscription_id).first()
    if not member:
        print(f"Unknown member from subscription ID {subscription_id}")
        return

    member.stripe_subscription_active = False
    member.save()

    member.update_wahf_group_membership()

    send_membership_error_email(
        f"WAHF Membership Subscription Cancelled - {member} {member.email}",
        f"Stripe notified us that payments failed or subscription was cancelled for {member.pk} {member} {member.email}",
    )
