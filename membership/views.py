import stripe
from django.http import JsonResponse

from membership.utils import get_stripe_secret_key

from .models import MembershipLevel

stripe.api_key = get_stripe_secret_key()


def create_payment_intent(request):
    # TODO these errors should return JSON

    slug = request.POST.get("membership-level-slug", None)
    if not slug:
        raise Exception("I don't know that membership level.")

    try:
        level = MembershipLevel.objects.get(slug=slug)
    except MembershipLevel.DoesNotExist:
        raise Exception("That membership level does not exist.")

    try:
        intent = stripe.PaymentIntent.create(
            amount=level.price * 1000,
            currency="usd",
            automatic_payment_methods={
                "enabled": True,
            },
        )
    except Exception:
        raise Exception("An error occured at our payment processor.")

    return JsonResponse({"clientSecret": intent["client_secret"]})
