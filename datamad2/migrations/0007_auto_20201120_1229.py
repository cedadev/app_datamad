# Generated by Django 2.2.13 on 2020-11-20 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamad2', '0006_grant_date_added'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importedgrant',
            name='parent_grant',
        ),
        migrations.AddField(
            model_name='grant',
            name='parent_grant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_grant', to='datamad2.Grant'),
        ),
    ]
