# Generated by Django 2.2.6 on 2020-07-22 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamad2', '0021_auto_20200716_1623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importedgrant',
            name='ticket',
        ),
        migrations.AddField(
            model_name='grant',
            name='jira_ticket',
            field=models.URLField(blank=True, null=True),
        ),
    ]
