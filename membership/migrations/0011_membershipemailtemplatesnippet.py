# Generated by Django 4.1.7 on 2023-05-23 13:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("membership", "0010_membershipregistration_member"),
    ]

    operations = [
        migrations.CreateModel(
            name="MembershipEmailTemplateSnippet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.CharField(max_length=200, unique=True)),
                ("subject", models.CharField(max_length=800)),
                ("body", models.TextField()),
            ],
            options={
                "verbose_name_plural": "Email Templates",
            },
        ),
    ]
