# Generated by Django 4.2.13 on 2024-06-19 14:10

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_ad_image_ad_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
