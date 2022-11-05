from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class BaseModel(models.Model):

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    updated = models.DateTimeField(
        auto_now=True,
        editable=False
    )

    @property
    def admin_change_url(self):
        if self.pk:
            return reverse('admin:%s_%s_change' % (
                self._meta.app_label,
                self._meta.model_name
            ), args=[self.pk])
        return None
    
    @property
    def admin_change_link(self):
        return mark_safe('<span><a href="%s" target="_blank">%s</a></span>' % (self.admin_change_url, self))

    class Meta:
        abstract = True

class LegalNameModel(models.Model):

    class NamePrefix(models.TextChoices):
        PREFIX_MISS = 'MS', _('Ms.')
        PREFIX_MRS = 'MRS', _('Mrs.')
        PREFIX_MR = 'MR', _('Mr.')
        PREFIX_MX = 'MX', _('Mx.')
        PREFIX_DR = 'DR', _('Dr.')
        PREFIX_REV = 'REV', _('Rev.')
        PREFIX_PROF = 'PROF', _('Prof.')
        PREFIX_HONORABLE = 'HNR', _('Hon.')
        PREFIX_MONSIGNOR = 'MSGR', _('Msgr.')
        PREFIX_RIGHT_HONORABLE = 'RTHNR', _('Rt. Hon.')

    first_name = models.CharField(max_length=200, blank=False, null=False)
    middle_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=False, null=False)
    suffix = models.CharField(max_length=200, blank=True)
    prefix = models.CharField(max_length=5, choices=NamePrefix.choices, default=NamePrefix.PREFIX_MISS)

    class Meta:
        abstract = True


class ContactInfoModel(models.Model):
    email_address = models.CharField(max_length=200, blank=True)
    primary_phone_number = PhoneNumberField(blank=True)
    mobile_phone_number = PhoneNumberField(blank=True)
    home_phone_number = PhoneNumberField(blank=True)
    fax_number = PhoneNumberField(blank=True)
    work_number = PhoneNumberField(blank=True)

	class Meta:
		abstract = True

class Student(BaseModel, LegalNameModel, ContactInfoModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class StudentIdentificationDocument(BaseModel):
	student = models.ForeignKey(Student, null=False, on_delete=models.CASCADE)
	document = models.FileField(upload_to='uploads/%Y/%m/%d/')
    document_title = models.CharField(max_length=300)
    document_description = models.TextField(default='')

class Course(BaseModel):
    name = models.CharField(max_length=200)
    enforce_minimum_time = models.BooleanField(default=False,
 		help_text='Does the student have to spend a certain amount of time to complete?')
    minimum_time_seconds = models.BigIntegerField(default=settings.MINIMUM_COURSE_SECONDS_DEFAULT,
 		help_text='Minimum time a student has to spend reading for a course to be considered complete')
    maximum_idle_time_seconds = models.BigIntegerField(default=settings.MAX_COURSE_IDLE_TIME_SECONDS,
 		help_text='Maximum time spent with no inputs before user is considered AFK')

class CoursePage(BaseModel):
    course = models.ForeignKey(Course, default=None, on_delete=models.CASCADE)
    page_number = models.IntegerField(default=1, help_text='Order of the page')
    page_title = models.CharField(max_length=200, help_text='Title of the page')
    page_contents = models.TextField(default="", help_text='''
 	The contents of your page. Regular paragraphs will work as expected
 	However, this is interpreted in markdown, so you can add extra styling
 	https://www.markdownguide.org/cheat-sheet/
 	''')

class CourseViewInstance(BaseModel):
    student = models.ForeignKey(Student, default=None, on_delete=models.CASCADE)
    course_view_start = models.DateTimeField(null=True)
    course_view_stop = models.DateTimeField(null=True)
    total_seconds_spent = models.BigIntegerField(default=0)

class CoursePageViewInstance(BaseModel):
    course_view_instance = models.ForeignKey(CourseViewInstance, default=None, on_delete=models.CASCADE)
    page_view_start = models.DateTimeField(null=True)
    course_page = models.ForeignKey(CoursePage, default=None, on_delete=models.CASCADE)
    total_seconds_spent = models.BigIntegerField(default=0)

class CourseTest(BaseModel):
    course = models.ForeignKey(Course, default=None, on_delete=models.CASCADE)
    test_is_timed = models.BooleanField(default=False, help_text='Is the test timed?')
    maximum_time_seconds = models.BigIntegerField(default=settings.MAXIMUM_TEST_SECONDS_DEFAULT,
 		help_text='''
 		The maximum time a user has on the test. All selected answers before this
 		time has passed will be recorded so incomplete tests will still have saved
 		the answers so far. "Test is timed" must be checked
 		''')
    is_course_fixed_answer_length = models.BooleanField(default=False,
 		help_text='If you want all answers in the test to have a fixed length')
    course_fixed_answer_length = models.IntegerField(default=settings.DEFAULT_MULTIPLE_CHOICE_LENGTH,
 		help_text='The fixed length of the answers if "Is course fixed answer length" is checked')
    order = models.IntegerField(default=1)
    allow_practice_tests = models.BooleanField(default=True, help_text='Turn practice tests on or off')
    maximum_practice_tests = models.IntegerField(default=0, help_text='''
 		Maximum number of practice tests. 0 is infinite. If you want 0 tests uncheck allow practice tests
 	''')


class MultipleChoiceAnswer(BaseModel):
    value = models.CharField(max_length=300, help_text='What shows up on the multiple choice answer')
    # used for random generation ordering
    # combo a and b or other combos needs design
    is_all_of_the_above = models.BooleanField(default=False, help_text='Does this answer mean all of the above?')
    is_none_of_the_above = models.BooleanField(default=False, help_text='Does this answer mean none of the above?')
    # random generation define smaller set of questions for live tests or practice
    is_live_only = models.BooleanField(default=False, help_text='This question is only for live tests')
    is_practice_only = models.BooleanField(default=False, help_text='This question is only for practice tests')

class MultipleChoiceTestQuestion(BaseModel):
    course_test = models.ForeignKey(CourseTest, default=None, on_delete=models.CASCADE)
    question_contents = models.TextField(default='', help_text='what the question will say')
    correct_multiple_choice_answer = models.ForeignKey(MultipleChoiceAnswer, default=None, on_delete=models.CASCADE)
    other_multiple_choice_answers = models.ManyToManyField(MultipleChoiceAnswer, related_name='course_tests',
		help_text='List of potential answers to appear in random generation')
    multiple_choice_answer_length = models.IntegerField(default=settings.DEFAULT_MULTIPLE_CHOICE_LENGTH,
		help_text = 'Total number of answers that will appear in the questions generated')

class CourseTestInstance(BaseModel):
    is_practice = models.BooleanField(default=False)
    course_test = models.ForeignKey(CourseTest, default=None, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, default=None, on_delete=models.CASCADE)
    test_started_on = models.DateTimeField(null=True)
    test_finished_on = models.DateTimeField(null=True)

class CourseTestAnswerInstance(BaseModel):
    course_test_instance = models.ForeignKey(CourseTestInstance, default=None, on_delete=models.CASCADE)
    question = models.ForeignKey(MultipleChoiceTestQuestion, default=None, on_delete=models.CASCADE)
    answer_chosen = models.ForeignKey(MultipleChoiceAnswer, default=None, on_delete=models.CASCADE)
    answer_chosen_on = models.DateTimeField(default=None)

