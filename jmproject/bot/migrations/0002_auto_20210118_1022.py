# Generated by Django 3.0.5 on 2021-01-18 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='candle_size',
            field=models.CharField(choices=[('1m', '1m'), ('3m', '3m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'), ('1h', '1h'), ('2h', '2h'), ('4h', '4h'), ('6h', '6h'), ('8h', '8h'), ('12h', '12h'), ('1d', '1d'), ('3d', '3d')], default='5m', help_text='The interval of time to consider as a single price data point', max_length=50, verbose_name='Candle Size'),
        ),
        migrations.AlterField(
            model_name='bot',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
    ]