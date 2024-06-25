# Generated by Django 5.0.3 on 2024-06-24 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0039_billing_bill_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billing',
            name='bill_image',
        ),
        migrations.AddField(
            model_name='billing',
            name='bill_image_data',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
