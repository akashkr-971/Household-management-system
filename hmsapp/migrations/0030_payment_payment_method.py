# Generated by Django 5.0.3 on 2024-05-22 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0029_payment_order_id_payment_razorpay_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(default='card', max_length=100),
        ),
    ]
