from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from membership.models import MembershipLevel
from users.models import Member
from users.utils import send_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        levels = MembershipLevel.objects.exclude(
            Q(name__icontains="Inductee")
            | Q(name__icontains="Lifetime")
            | Q(name__icontains="Staff")
        )

        member_qs = Member.objects.filter(
            membership_level__in=levels,
            stripe_subscription_id="",
            membership_expiry_date__lt=(timezone.now() + timedelta(days=60)),
            membership_renewal_reminder_date__isnull=True,
        )

        for member in member_qs:
            body = render_to_string(
                "emails/member_renewal_notice.html", {"member": member}
            )

            send_email(
                to=[member.email],
                subject="Membership Renewal - Wisconsin Aviation Hall of Fame",
                body=None,
                body_html=body,
                context={
                    "member": member,
                },
            )

            member.membership_renewal_reminder_date = timezone.now().date()
            member.save()
