# Generated by Django 2.0.6 on 2018-11-10 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_auto_20181109_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='contract_address',
            field=models.CharField(blank=True, max_length=44, null=True, unique=True),
        ),
    ]
