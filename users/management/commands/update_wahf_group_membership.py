from django.core.management.base import BaseCommand

from users.models import Member
from users.utils import get_wahf_group


class Command(BaseCommand):
    def handle(self, *args, **options):
        group = get_wahf_group()

        for m in Member.objects.select_related("user").all():
            result = m.update_wahf_group_membership(group=group)

            if result:
                print(m.user, " + OK")
            else:
                print(m.user, " ---- expired")
