from django.conf import settings


def environment_name(request):
    # production/staging/development
    return {"environment_name": settings.ENVIRONMENT_NAME}
