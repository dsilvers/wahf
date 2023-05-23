# Generated by Django 4.1.7 on 2023-05-23 01:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0018_member_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="membership_join_date",
            field=models.DateField(
                blank=True, help_text="The date they joined WAHF.", null=True
            ),
        ),
    ]
