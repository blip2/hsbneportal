# Generated by Django 2.0.7 on 2018-07-20 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doors',
            name='last_seen',
        ),
    ]
