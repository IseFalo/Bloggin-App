# Generated by Django 5.0 on 2024-03-08 18:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0050_post_status_delete_draftedpost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='series',
            name='series_posts',
        ),
        migrations.AddField(
            model_name='post',
            name='series',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.series'),
        ),
        migrations.AddField(
            model_name='series',
            name='description',
            field=models.TextField(null=True),
        ),
    ]