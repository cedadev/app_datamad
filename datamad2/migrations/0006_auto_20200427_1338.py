# Generated by Django 2.2.10 on 2020-04-27 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamad2', '0005_auto_20200427_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datacentre',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
