from django.conf import settings
from django.template.loader import render_to_string

from users.utils import send_email


def get_stripe_public_key():
    if settings.STRIPE_LIVE_MODE:
        if not settings.STRIPE_LIVE_PUBLIC_KEY:
            raise Exception("STRIPE_LIVE_PUBLIC_KEY not set")
        return settings.STRIPE_LIVE_PUBLIC_KEY

    if not settings.STRIPE_TEST_PUBLIC_KEY:
        raise Exception("STRIPE_TEST_PUBLIC_KEY not set")
    return settings.STRIPE_TEST_PUBLIC_KEY


def get_stripe_secret_key():
    if settings.STRIPE_LIVE_MODE:
        if not settings.STRIPE_LIVE_SECRET_KEY:
            raise Exception("STRIPE_LIVE_SECRET_KEY not set")
        return settings.STRIPE_LIVE_SECRET_KEY

    if not settings.STRIPE_TEST_SECRET_KEY:
        raise Exception("STRIPE_TEST_SECRET_KEY not set")
    return settings.STRIPE_TEST_SECRET_KEY


def send_membership_error_email(subject, error):
    alert_body = render_to_string("emails/membership_error.html", {"error": error})

    send_email(
        to=["membership@wahf.org", "dan@wahf.org"],
        subject=subject,
        body=None,
        body_html=alert_body,
    )
