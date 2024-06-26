# Generated by Django 5.0.3 on 2024-05-24 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0033_alter_reviews_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='method',
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('Bill created', 'Bill created'), ('Paid', 'Paid')], default='Pending', max_length=20),
        ),
    ]
