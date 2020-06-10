# Generated by Django 2.2.10 on 2020-05-05 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamad2', '0009_auto_20200505_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('upload', models.FileField(upload_to='')),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('checksum', models.CharField(blank=True, max_length=100)),
                ('grant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datamad2.Grant')),
            ],
        ),
        migrations.CreateModel(
            name='DMPDocument',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='datamad2.Document')),
                ('version', models.CharField(max_length=100)),
            ],
            bases=('datamad2.document',),
        ),
    ]
