# Generated by Django 5.1.3 on 2024-12-07 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0010_review'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Review',
        ),
    ]