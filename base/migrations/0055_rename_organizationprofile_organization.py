# Generated by Django 5.0 on 2024-03-14 06:42

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0054_organizationprofile_profile_img'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrganizationProfile',
            new_name='Organization',
        ),
    ]