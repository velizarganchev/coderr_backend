# Generated by Django 5.1.3 on 2024-12-07 15:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_app', '0003_alter_review_business_user_alter_review_reviewer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='business_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_for_business', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='review',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_by_user', to=settings.AUTH_USER_MODEL),
        ),
    ]