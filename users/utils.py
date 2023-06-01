from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from usps import Address, USPSApi, USPSApiError


def usps_validate_user_address(user):
    if not settings.USPS_USERNAME:
        raise Exception("USPS_USERNAME is not set in settings")

    usps = USPSApi(settings.USPS_USERNAME)
    address = Address(
        name=f"{user.first_name} {user.last_name}",
        address_1=user.address_line1,
        address_2=user.address_line2,
        city=user.city,
        state=user.state,
        zipcode=user.zip,
    )

    try:
        validation = usps.validate_address(address)
    except USPSApiError:
        return user

    usps_validation_result = validation.result

    try:
        usps_validation_result["AddressValidateResponse"]["Address"]["Error"]
    except KeyError:
        usps_address = usps_validation_result["AddressValidateResponse"]["Address"]
    else:
        return user

    user.address_line1 = usps_address["Address2"]
    user.address_line2 = (
        "" if usps_address["Address1"] == "-" else usps_address["Address1"]
    )
    user.city = usps_address["City"].title()
    user.state = usps_address["State"]
    if usps_address["Zip4"]:
        user.zip = f"{usps_address['Zip5']}-{usps_address['Zip4']}"
    user.save()

    return user


def get_wahf_group():
    group, created = Group.objects.get_or_create(name="WAHF Members")
    return group


def send_email(to, subject, body, context={}, body_html=None):
    if type(to) is str:
        to = [to]

    if not body_html:
        body_template = Template(body)
        body_context = Context(context)
        body_html = body_template.render(body_context)

    html_message = render_to_string("emails/base.html", {"body": body_html})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL

    mail.send_mail(
        subject,
        plain_message,
        from_email,
        to,
        html_message=html_message,
        fail_silently=False,
    )
