# Generated by Django 5.0.3 on 2024-05-02 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0013_booking_landmark_booking_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Completed', 'Compl;eted')], default='Pending', max_length=20),
        ),
    ]
