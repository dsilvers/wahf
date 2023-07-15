import csv
from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.template.loader import render_to_string

from membership.models import MembershipLevel
from users.models import Member, User
from users.utils import send_email


def get_level(slug):
    return MembershipLevel.objects.get(slug=slug)


def get_levels_map():
    return {
        "Annual": get_level("individual"),
        "Family": get_level("individual-spouse"),
        "Life": get_level("lifetime-individual"),
        "Life Fam": get_level("lifetime-spouse"),
        "Youth": get_level("individual-youth"),
        "Corporate": get_level("biz-small"),
        "Inductee": get_level("inductee"),
    }


def send_invite_email(member, password):
    body = render_to_string(
        "emails/member_import_invite.html", {"member": member, "password": password}
    )

    send_email(
        to=[member.email],
        subject="Wisconsin Aviation Hall of Fame - New Website!",
        body=None,
        body_html=body,
        context={
            "member": member,
        },
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("membership_file", nargs="+", type=str)

    def handle(self, *args, **options):
        levels = get_levels_map()

        member_data = []

        for membership_file in options["membership_file"]:
            with open(membership_file) as csvfile:
                csvreader = csv.reader(csvfile)
                count = 0
                for row in csvreader:
                    count += 1
                    if count == 1:
                        continue

                    level_raw = row[1].strip()
                    if level_raw == "Annual Ind":
                        level_raw = "Annual"

                    level = None
                    if "induct" in level_raw.lower():
                        level = levels["Inductee"]
                    else:
                        level = levels.get(level_raw)

                    email = row[9]
                    if not email:
                        print(f"skipping row {row[0]}, as it has no email")
                    elif not level:
                        print(f"{level_raw} not mapped")
                    elif User.objects.filter(email__iexact=email).exists():
                        print(f"{email} exists in users table already")
                    else:
                        member_data.append(
                            {
                                "level": level,
                                "first_name": row[2],
                                "last_name": row[3],
                                "address": row[4],
                                "city": row[5],
                                "state": row[6],
                                "zip": row[7],
                                "date_joined": datetime.strptime(
                                    row[8], "%m/%d/%y"
                                ).date()
                                if row[8]
                                else None,
                                "email": email,
                                "phone": row[10],
                            }
                        )

        for d in member_data:
            print(f"+ {d['email']}")
            random_digits = User.objects.make_random_password(
                length=4, allowed_chars="23456789"
            )
            password = f"wahf{random_digits}"
            try:
                user = User.objects.create_user(
                    email=d["email"].lower(),
                    password=password,
                )
            except IntegrityError:
                print(f"ERROR importing {d['email']}")
                continue

            member = Member.objects.create(
                **{
                    "user": user,
                    "email": d["email"].lower(),
                    "membership_level": d["level"],
                    "membership_join_date": d["date_joined"],
                    "last_payment_date": date(2023, 1, 1),
                    "membership_expiry_date": date(2023, 12, 31),
                    "first_name": d["first_name"],
                    "last_name": d["last_name"],
                    "business_name": "",
                    "spouse_name": "",
                    "address_line1": d["address"],
                    "address_line2": "",
                    "city": d["city"],
                    "state": d["state"],
                    "zip": d["zip"],
                    "phone": d["phone"],
                }
            )

            send_invite_email(member, password)
