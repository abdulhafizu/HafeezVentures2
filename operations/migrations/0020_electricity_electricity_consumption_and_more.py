# Generated by Django 4.2.7 on 2023-11-19 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0019_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='electricity',
            name='electricity_consumption',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='electricity',
            name='electricity_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='electricity',
            name='standard_electricity_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
