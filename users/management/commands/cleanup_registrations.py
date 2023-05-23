from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from membership.models import MembershipRegistration


class Command(BaseCommand):
    def handle(self, *args, **options):
        MembershipRegistration.objects.filter(
            created__lt=timezone.now() - timedelta(hours=24)
        ).delete()
