# Generated by Django 5.1.6 on 2025-02-17 12:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0025_alter_comment_date_alter_listing_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 17, 15, 11, 4, 599381)),
        ),
        migrations.AlterField(
            model_name='listing',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 17, 15, 11, 4, 598463)),
        ),
    ]
