# Generated by Django 4.2.7 on 2023-11-21 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0025_remove_electricity_electricity_variance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerin',
            name='customer_serial',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
