# Generated by Django 2.2.13 on 2020-08-04 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamad2', '0022_auto_20200729_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='preferred_facets',
            field=models.TextField(null=True),
        ),
    ]
