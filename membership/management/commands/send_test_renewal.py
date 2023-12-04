from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from users.models import Member
from users.utils import send_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        member = Member.objects.get(email="dan@silvers.net")

        body = render_to_string("emails/member_renewal_notice.html", {"member": member})

        send_email(
            to=[member.email, "rosedorceyFIF@gmail.com"],
            subject="Membership Renewal - Wisconsin Aviation Hall of Fame - TESTING",
            body=None,
            body_html=body,
            context={
                "member": member,
            },
        )
