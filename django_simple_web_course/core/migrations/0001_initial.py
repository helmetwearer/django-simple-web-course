# Generated by Django 4.1.3 on 2022-11-07 17:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('enforce_minimum_time', models.BooleanField(default=False, help_text='Does the student have to spend a certain amount of time to complete?')),
                ('minimum_time_seconds', models.BigIntegerField(default=7200, help_text='Minimum time a student has to spend reading for a course to be considered complete')),
                ('maximum_idle_time_seconds', models.BigIntegerField(default=900, help_text='Maximum time spent with no inputs before user is considered AFK')),
                ('published', models.BooleanField(default=False, help_text='Course is ready to appear on the home page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoursePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('page_number', models.IntegerField(default=1, help_text='Order of the page')),
                ('page_title', models.CharField(help_text='Title of the page', max_length=200)),
                ('page_contents', models.TextField(default='', help_text='\n     \tThe contents of your page. Regular paragraphs will work as expected\n     \tHowever, this is interpreted in markdown, so you can add extra styling<br/>\n     \t<a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">\n        Click Here for a Markdown Cheat Sheet</a>\n     \t')),
                ('course', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.course')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('test_is_timed', models.BooleanField(default=False, help_text='Is the test timed?')),
                ('maximum_time_seconds', models.BigIntegerField(default=3600, help_text='\n \t\tThe maximum time a user has on the test. All selected answers before this\n \t\ttime has passed will be recorded so incomplete tests will still have saved\n \t\tthe answers so far. "Test is timed" must be checked\n \t\t')),
                ('is_course_fixed_answer_length', models.BooleanField(default=False, help_text='If you want all answers in the test to have a fixed length')),
                ('course_fixed_answer_length', models.IntegerField(default=4, help_text='The fixed length of the answers if "Is course fixed answer length" is checked')),
                ('order', models.IntegerField(default=1)),
                ('allow_practice_tests', models.BooleanField(default=True, help_text='Turn practice tests on or off')),
                ('maximum_practice_tests', models.IntegerField(default=0, help_text='\n \t\tMaximum number of practice tests. 0 is infinite. If you want 0 tests uncheck allow practice tests\n \t')),
                ('course', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.course')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultipleChoiceAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(help_text='What shows up on the multiple choice answer', max_length=300)),
                ('is_all_of_the_above', models.BooleanField(default=False, help_text='Does this answer mean all of the above?')),
                ('is_none_of_the_above', models.BooleanField(default=False, help_text='Does this answer mean none of the above?')),
                ('is_live_only', models.BooleanField(default=False, help_text='This question is only for live tests')),
                ('is_practice_only', models.BooleanField(default=False, help_text='This question is only for practice tests')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('prefix', models.CharField(choices=[('', ''), ('MS', 'Ms.'), ('MRS', 'Mrs.'), ('MR', 'Mr.'), ('MX', 'Mx.'), ('DR', 'Dr.'), ('REV', 'Rev.'), ('PROF', 'Prof.'), ('HNR', 'Hon.'), ('MSGR', 'Msgr.'), ('RTHNR', 'Rt. Hon.')], default='', max_length=5)),
                ('first_name', models.CharField(max_length=200)),
                ('middle_name', models.CharField(blank=True, max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('suffix', models.CharField(blank=True, max_length=200)),
                ('email_address', models.CharField(blank=True, max_length=200)),
                ('primary_phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('mobile_phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('home_phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('fax_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('work_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentIdentificationDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('document', models.FileField(blank=True, help_text="The file for the student's document", upload_to='uploads/%Y/%m/%d/')),
                ('document_title', models.CharField(help_text='Name of the document. (comes from site settings)', max_length=300)),
                ('document_description', models.TextField(default='', help_text='Description of the document (comes from site settings)')),
                ('verification_required', models.BooleanField(default=False, help_text='Do we need to verify this document before the student can begin classes')),
                ('verified', models.BooleanField(default=False, help_text='Has the document been verified')),
                ('student', models.ForeignKey(help_text='Student the document belongs to', on_delete=django.db.models.deletion.CASCADE, to='core.student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultipleChoiceTestQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('question_contents', models.TextField(default='', help_text='what the question will say')),
                ('multiple_choice_answer_length', models.IntegerField(default=4, help_text='Total number of answers that will appear in the questions generated')),
                ('correct_multiple_choice_answer', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.multiplechoiceanswer')),
                ('course_test', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.coursetest')),
                ('other_multiple_choice_answers', models.ManyToManyField(help_text='List of potential answers to appear in random generation', related_name='course_tests', to='core.multiplechoiceanswer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseViewInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('course_view_start', models.DateTimeField(null=True)),
                ('course_view_stop', models.DateTimeField(null=True)),
                ('total_seconds_spent', models.BigIntegerField(default=0)),
                ('student', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseTestInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('is_practice', models.BooleanField(default=False)),
                ('test_started_on', models.DateTimeField(null=True)),
                ('test_finished_on', models.DateTimeField(null=True)),
                ('available_answers', models.ManyToManyField(related_name='course_test_instances', to='core.multiplechoiceanswer')),
                ('course_test', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.coursetest')),
                ('student', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseTestAnswerInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('answer_chosen_on', models.DateTimeField(default=None)),
                ('answer_chosen', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.multiplechoiceanswer')),
                ('course_test_instance', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.coursetestinstance')),
                ('question', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.multiplechoicetestquestion')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoursePageViewInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('page_view_start', models.DateTimeField(null=True)),
                ('total_seconds_spent', models.BigIntegerField(default=0)),
                ('course_page', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.coursepage')),
                ('course_view_instance', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.courseviewinstance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CoursePageMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(upload_to='pagemedia/%Y/%m/%d/')),
                ('course_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.coursepage')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
