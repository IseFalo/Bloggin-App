# Generated by Django 5.0 on 2024-03-12 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0053_organizationprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationprofile',
            name='profile_img',
            field=models.ImageField(default='blank-profile-picture.png', upload_to='profile_images'),
        ),
    ]