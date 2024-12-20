# Generated by Django 4.2.8 on 2024-11-02 04:17

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("content", "0014_remove_articlepage_byline_articleauthor_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="KohnProjectPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("funding_percent_raised", models.FloatField(blank=True, null=True)),
                (
                    "funding_dollars_raised",
                    models.SmallIntegerField(blank=True, null=True),
                ),
                ("funding_goal", models.SmallIntegerField(blank=True, null=True)),
                (
                    "business_donors",
                    wagtail.fields.RichTextField(
                        blank=True, help_text="A list of businesses that have donated."
                    ),
                ),
                (
                    "individual_donors",
                    wagtail.fields.RichTextField(
                        blank=True, help_text="A list of individuals that have donated."
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
