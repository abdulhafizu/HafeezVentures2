# Generated by Django 4.2.7 on 2023-11-16 03:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0007_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recyclingoperation',
            old_name='meter_reading',
            new_name='meter_ID',
        ),
    ]
