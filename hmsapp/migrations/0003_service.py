# Generated by Django 5.0.3 on 2024-04-25 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0002_rename_user_id_homeowner_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('service_id', models.AutoField(primary_key=True, serialize=False)),
                ('service_name', models.CharField(max_length=20)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
