# Generated by Django 4.1.7 on 2023-07-15 06:00

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("magazine", "0003_magazinepage_magazinepage_issuepageuniquetogether"),
    ]

    operations = [
        TrigramExtension(),
    ]
