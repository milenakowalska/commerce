# Generated by Django 3.0.2 on 2020-09-29 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20200929_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_price',
            field=models.IntegerField(default=models.IntegerField()),
        ),
    ]