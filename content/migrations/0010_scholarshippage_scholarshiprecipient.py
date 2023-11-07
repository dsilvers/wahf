# Generated by Django 4.1.7 on 2023-10-14 16:24

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models

import wahf.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("archives", "0011_remove_collectiongallery_name"),
        ("wagtailcore", "0083_workflowcontenttype"),
        ("content", "0009_alter_inducteedetailpage_body"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScholarshipPage",
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
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            (
                                "heading",
                                wagtail.blocks.CharBlock(form_classname="title"),
                            ),
                            ("paragraph", wagtail.blocks.RichTextBlock()),
                            ("image", wagtail.images.blocks.ImageChooserBlock()),
                        ],
                        blank=True,
                        use_json_field=True,
                    ),
                ),
                ("contribute_link", models.CharField(blank=True, max_length=500)),
                (
                    "top_images",
                    wagtail.fields.StreamField(
                        [("image", wagtail.images.blocks.ImageChooserBlock())],
                        blank=True,
                        use_json_field=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(wahf.mixins.OpenGraphMixin, "wagtailcore.page"),
        ),
        migrations.CreateModel(
            name="ScholarshipRecipient",
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
                ("year", models.PositiveSmallIntegerField(help_text="example: 2023")),
                (
                    "scholarship_name",
                    models.CharField(
                        help_text="example: 'Test Person Scholarship'", max_length=250
                    ),
                ),
                ("recipient_name", models.CharField(max_length=150)),
                (
                    "blurb",
                    wagtail.fields.RichTextField(
                        help_text="A longer description of this gallery. Displayed on the gallery detail page."
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Scholarship recipient photo.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="archives.wahfimage",
                    ),
                ),
            ],
        ),
    ]