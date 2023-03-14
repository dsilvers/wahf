from django.conf import settings


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
