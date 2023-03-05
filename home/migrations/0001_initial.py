# Generated by Django 4.1.7 on 2023-03-05 05:23

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models

import wahf.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("content", "0001_initial"),
        ("wagtailcore", "0083_workflowcontenttype"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePage",
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
                ("non_member_headline", models.TextField()),
                ("non_member_blurb", wagtail.fields.RichTextField()),
                ("non_member_link_text", models.CharField(blank=True, max_length=200)),
                (
                    "non_member_image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="content.wahfimage",
                    ),
                ),
                (
                    "non_member_link_page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(wahf.mixins.OpenGraphMixin, "wagtailcore.page"),
        ),
        migrations.CreateModel(
            name="HomePageCardItem",
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
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("tagline", models.CharField(blank=True, max_length=255)),
                ("heading", models.CharField(max_length=255)),
                ("blurb", wagtail.fields.RichTextField()),
                ("date", models.DateField(blank=True, null=True)),
                ("link_text", models.CharField(blank=True, max_length=255)),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="content.wahfimage",
                    ),
                ),
                (
                    "link_page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="home_page_cards",
                        to="home.homepage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
