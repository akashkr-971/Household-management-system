# Generated by Django 5.0.3 on 2024-05-03 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0020_booking_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='jobdescription',
            field=models.TextField(default='None'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed')], default='Pending', max_length=20),
        ),
    ]
