# Generated by Django 4.2.3 on 2023-08-18 10:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0026_profile_top_picks'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='following', to=settings.AUTH_USER_MODEL),
        ),
    ]