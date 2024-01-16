import csv

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from users.models import Member
from users.utils import send_email


def send_reminder(member):
    if (
        member.membership_expiry_date
        and member.membership_expiry_date > timezone.now().date()
    ):
        print("Not up for renewal: ", member.email)
        return

    body = render_to_string("emails/member_renewal_reminder.html", {"member": member})

    send_email(
        to=[member.email],
        subject="Urgent — Your WAHF Membership Renewal is Past Due!",
        body=None,
        body_html=body,
        context={
            "member": member,
        },
    )

    print("OK", member.email)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("membership_file", nargs="+", type=str)

    def handle(self, *args, **options):
        for membership_file in options["membership_file"]:
            with open(membership_file) as csvfile:
                csvreader = csv.reader(csvfile)
                count = 0
                for row in csvreader:
                    count += 1
                    if count == 1:
                        continue

                    email = row[0]

                    try:
                        member = Member.objects.get(email__iexact=email)
                    except Member.DoesNotExist:
                        print("Member not found: ", email)
                    else:
                        send_reminder(member)
