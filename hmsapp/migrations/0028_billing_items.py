# Generated by Django 5.0.3 on 2024-05-15 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0027_booking_totalrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='billing',
            name='items',
            field=models.JSONField(default=list),
        ),
    ]
