# Generated by Django 5.0.3 on 2024-06-25 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0042_alter_billing_bill_image_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='bill_image_data',
            field=models.ImageField(blank=True, null=True, upload_to='bill_images/'),
        ),
    ]
