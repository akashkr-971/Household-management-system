# Generated by Django 5.0.3 on 2024-05-02 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0016_booking_jobdescription'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviceprovider',
            old_name='Profession',
            new_name='profession',
        ),
    ]
