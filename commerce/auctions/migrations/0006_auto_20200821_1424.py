# Generated by Django 3.1 on 2020-08-21 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20200821_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='listing_detail',
            field=models.TextField(max_length=800),
        ),
    ]