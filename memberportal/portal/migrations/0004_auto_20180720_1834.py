# Generated by Django 2.0.7 on 2018-07-20 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_doors_last_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doors',
            name='last_seen',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
