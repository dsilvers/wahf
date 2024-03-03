import json

import stripe
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from membership.models import MembershipEmailTemplateSnippet
from membership.utils import get_stripe_secret_key_donations
from users.utils import send_email

# FOR DONATIONS ONLY HERE
# This stripe account is dedicated towards donations.
stripe.api_key = get_stripe_secret_key_donations()


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

        if action == "kohn":
            process_kohn_donation(event.data.object, session)
        elif action == "donation":
            process_donation_payment(event.data.object, session)

    return HttpResponse(status=200)


def process_kohn_donation(obj, session):
    # Total amount paid
    amount_total = session["amount_total"] / 100.0

    name = session["customer_details"]["name"]
    email = session["customer_details"]["email"]

    stripe_id = session["id"]

    confirmation_body = render_to_string(
        "emails/kohn_thanks.html",
        {
            "amount": amount_total,
            "name": name,
            "transaction_id": stripe_id,
        },
    )

    send_email(
        to=[email],
        subject="Thanks for your support - Leo J. Kohn Photograph Collection",
        body=None,
        body_html=confirmation_body,
        context={
            "email": email,
        },
        from_email="WAHF/Kohn <kohn@wahf.org>",
    )

    send_email(
        to=["kohn@wahf.org"],
        subject="Thanks for your support - Leo J. Kohn Photograph Collection",
        body=None,
        body_html=confirmation_body,
        context={
            "email": email,
        },
        from_email="WAHF/Kohn <kohn@wahf.org>",
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