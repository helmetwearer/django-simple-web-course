# Generated by Django 4.1.3 on 2022-11-16 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursetestquestionanswerinstance',
            name='question_instance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_test_answer_instances', to='core.coursetestquestioninstance'),
        ),
    ]
