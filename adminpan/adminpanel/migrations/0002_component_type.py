# Generated by Django 5.1 on 2024-08-23 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='type',
            field=models.CharField(default='text', max_length=100),
            preserve_default=False,
        ),
    ]