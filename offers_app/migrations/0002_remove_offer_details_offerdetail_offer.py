# Generated by Django 5.1.3 on 2024-12-02 20:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='details',
        ),
        migrations.AddField(
            model_name='offerdetail',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='details', to='offers_app.offer'),
        ),
    ]
