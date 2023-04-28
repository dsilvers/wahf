import json
import uuid
from datetime import datetime

import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from membership.models import MembershipLevel, MembershipRegistration
from membership.utils import get_stripe_secret_key
from users.models import User
from users.utils import usps_validate_user_address

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

    return HttpResponse(status=200)


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
        return

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
        **{
            "membership_level": MembershipLevel.objects.get(
                id=reg.data["membership_level"]
            ),
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

    user.password = reg.data["password_hash"]
    user.save()

    # Attempt to validate the address
    user = usps_validate_user_address(user)

    # Handle automatic payments (disable subscription if they didn't want autopay)
    if not user.membership_automatic_payment:
        stripe.Subscription.modify(
            user.stripe_subscription_id, cancel_at_period_end=True
        )

    # Send a welcome email

    reg.delete()
