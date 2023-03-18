# Generated by Django 4.1.7 on 2023-03-18 17:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("magazine", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="magazineissuepage",
            name="issue_number",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="magazineissuepage",
            name="volume_number",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
