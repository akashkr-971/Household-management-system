# Generated by Django 5.0.3 on 2024-04-25 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hmsapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homeowner',
            old_name='user_id',
            new_name='user',
        ),
    ]
