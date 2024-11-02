import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from sentry_sdk import capture_exception

from membership.utils import get_stripe_secret_key_donations


class KohnDonateRedirect(View):
    permanent = False
    query_string = False

    def get(self, *args, **kwargs):
        price_lookup = kwargs.get("price", None)

        default = "price_1Op2YKE1FfEWhMfKEIuTGPxO"
        price_map = {
            25: "price_1Op2YjE1FfEWhMfKGbARLuMz",
            50: "price_1Op2YvE1FfEWhMfKUSC0RCaO",
            100: "price_1Op2Z6E1FfEWhMfKNZ6TutWv",
            250: "price_1Op2ZIE1FfEWhMfKPNNNwmr3",
            500: "price_1Op2ZSE1FfEWhMfKzYlQxr4F",
            750: "price_1Op2ZfE1FfEWhMfKmizSBjyg",
            1000: "price_1Op2ZpE1FfEWhMfKTkchmcY1",
            2000: "price_1Op2ZyE1FfEWhMfKc5xjLukk",
            3000: "price_1Op2aBE1FfEWhMfKFelTo00Z",
            5000: "price_1Op2aTE1FfEWhMfKAQjgkRg2",
            7500: "price_1Op2ahE1FfEWhMfKFCzm1dDD",
            10000: "price_1Op2awE1FfEWhMfKng7AGISe",
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
                api_key=get_stripe_secret_key_donations(),
            )
        except Exception as e:
            # if hasattr(e, "user_message"):
            #    # self.request.session["payment_error"] = e.user_message
            if settings.SENTRY_DSN:
                capture_exception(e)
            return HttpResponseRedirect("/kohn")

        response = HttpResponse(content="", status=303)
        response["Location"] = checkout_session.url
        return response
