# Generated by Django 3.1.7 on 2021-02-24 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210120_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='sorting_preference',
            field=models.CharField(default='-profit', max_length=100),
        ),
    ]