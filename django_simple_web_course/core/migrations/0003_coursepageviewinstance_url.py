# Generated by Django 4.1.3 on 2022-11-10 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_course_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursepageviewinstance',
            name='url',
            field=models.TextField(blank=True, default=''),
        ),
    ]
