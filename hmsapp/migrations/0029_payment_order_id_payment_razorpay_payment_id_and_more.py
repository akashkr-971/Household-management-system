# Generated by Django 5.0.3 on 2024-05-21 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0028_billing_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('Bill created', 'Bill created'), ('Finished', 'Finished')], default='Pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(default='Pending', max_length=100),
        ),
    ]