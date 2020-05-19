# Generated by Django 2.2.10 on 2020-05-05 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamad2', '0008_auto_20200427_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grant',
            name='assigned_data_centre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_data_centre', to='datamad2.DataCentre'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='other_data_centre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='other_data_centre', to='datamad2.DataCentre'),
        ),
    ]