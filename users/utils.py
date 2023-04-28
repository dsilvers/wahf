from django.conf import settings
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
    user.zip = f"{usps_address['Zip5']}-{usps_address['Zip4']}"
    user.save()

    return user
