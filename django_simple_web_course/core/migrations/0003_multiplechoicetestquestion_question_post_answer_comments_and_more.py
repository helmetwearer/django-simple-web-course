# Generated by Django 4.1.3 on 2022-11-18 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_coursetestquestionanswerinstance_question_instance'),
    ]

    operations = [
        migrations.AddField(
            model_name='multiplechoicetestquestion',
            name='question_post_answer_comments',
            field=models.TextField(default='', help_text='\n        Educational comments that will show only after the question is answered.\n        Regular paragraphs will work as expected\n        However, this is interpreted in markdown, so you can add extra styling<br/>\n        <a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">\n        Click Here for a Markdown Cheat Sheet</a>\n        '),
        ),
        migrations.AlterField(
            model_name='coursetestquestionanswerinstance',
            name='question_instance',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_test_answer_instance', to='core.coursetestquestioninstance'),
        ),
        migrations.AlterField(
            model_name='multiplechoicetestquestion',
            name='question_contents',
            field=models.TextField(default='', help_text='\n        The contents of your question. Regular paragraphs will work as expected\n        However, this is interpreted in markdown, so you can add extra styling<br/>\n        <a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">\n        Click Here for a Markdown Cheat Sheet</a>\n        '),
        ),
    ]