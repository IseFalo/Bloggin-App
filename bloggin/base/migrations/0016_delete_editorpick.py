# Generated by Django 4.2.3 on 2023-08-15 16:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_rename_post_editorpick_posts'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EditorPick',
        ),
    ]