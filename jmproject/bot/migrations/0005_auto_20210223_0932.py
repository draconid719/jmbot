# Generated by Django 3.1.7 on 2021-02-23 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_auto_20210223_0931'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='orderhistory',
            table='bot_order_history',
        ),
    ]
