# Generated by Django 3.1 on 2020-08-21 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200815_2016'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionlisting',
            name='image',
        ),
    ]