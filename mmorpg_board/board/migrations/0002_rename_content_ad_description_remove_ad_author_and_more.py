# Generated by Django 4.2.13 on 2024-06-19 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ad',
            old_name='content',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='ad',
            name='author',
        ),
        migrations.RemoveField(
            model_name='ad',
            name='created_at',
        ),
    ]
