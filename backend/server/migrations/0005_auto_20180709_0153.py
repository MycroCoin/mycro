# Generated by Django 2.0.6 on 2018-07-09 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_auto_20180705_0110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asc',
            name='address',
            field=models.CharField(max_length=42, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='dao_address',
            field=models.CharField(max_length=42, unique=True),
        ),
    ]