# Generated by Django 5.0.3 on 2024-05-24 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0034_remove_payment_method_alter_booking_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='order_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
