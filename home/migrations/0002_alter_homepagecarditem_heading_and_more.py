# Generated by Django 4.1.7 on 2023-03-03 20:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0001_initial"),
        ("wagtailcore", "0083_workflowcontenttype"),
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepagecarditem",
            name="heading",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="homepagecarditem",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="content.wahfimage",
            ),
        ),
        migrations.AlterField(
            model_name="homepagecarditem",
            name="link_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="wagtailcore.page",
            ),
        ),
    ]
