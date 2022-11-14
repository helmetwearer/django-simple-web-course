from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.safestring import mark_safe
from .managers import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from .email_dispatchers import dispatch_student_verification_email
from .utils import human_time_duration
import uuid

# Create your models here.
class BaseModel(models.Model):
    guid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    updated = models.DateTimeField(
        auto_now=True,
        editable=False
    )

    @property
    def guid_string(self):
        return str(self.guid)

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
        PREFIX_NONE = '', _('')
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

    prefix = models.CharField(max_length=5, choices=NamePrefix.choices, default=NamePrefix.PREFIX_NONE,
        blank=True)
    first_name = models.CharField(max_length=200, blank=False, null=False)
    middle_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=False, null=False)
    suffix = models.CharField(max_length=200, blank=True)

    @property
    def full_legal_name(self):
        # add all 5 parts of the name
        legal_name = '%s %s %s %s %s' % (
            self.get_prefix_display(), self.first_name, self.middle_name, self.last_name, self.suffix)
        # remove duplicate whitespace and return
        return ' '.join(legal_name.split())


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


class Student(LegalNameModel, ContactInfoModel, BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    verification_ready_on = models.DateTimeField(blank=True, null=True, editable=False)
    verified_on = models.DateTimeField(blank=True, null=True, editable=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, editable=False,
        on_delete=models.CASCADE, related_name='students')

    objects = StudentManager()


    @property
    def verification_url(self):
        if self.guid and self.verification_ready_on and not self.verified_on:
            return reverse('student_verification', kwargs={'student_guid':self.guid})
        return None

    @property
    def verification_link(self):
        url = self.verification_url
        if url is None:
            return ''
        return mark_safe('<span><a href="%s" target="_blank">Verify Student</a></span>' % (url))

    @property
    def is_verified(self):
        if self.verified_on:
            return True
        unverified_required_documents = StudentIdentificationDocument.objects.filter(pk=self.pk,
            verification_required=True, verified=False)
        return unverified_required_documents.count() == 0

    @property
    def document_forms(self):
        from .forms import StudentIdentificationDocumentForm
        from .models import StudentIdentificationDocument
        return [
            StudentIdentificationDocumentForm(instance=instance)
            for instance in StudentIdentificationDocument.objects.filter(student=self)
        ]

    def __str__(self):
        return self.full_legal_name

class StudentIdentificationDocument(BaseModel):

    objects = StudentIdentificationDocumentManager()

    student = models.ForeignKey(Student, null=False, on_delete=models.CASCADE,
        help_text="Student the document belongs to", related_name='student_identification_documents')
    document = models.FileField(upload_to='uploads/%Y/%m/%d/', blank=True,
        help_text="The file for the student's document")
    document_title = models.CharField(max_length=300,
        help_text="Name of the document. (comes from site settings)")
    document_description = models.TextField(default='',
        help_text="Description of the document (comes from site settings)")
    verification_required = models.BooleanField(default=False,
        help_text="Do we need to verify this document before the student can begin classes")
    verified = models.BooleanField(default=False,
        help_text="Has the document been verified")

    def __str__(self):
        return '%s %s' % (self.student.full_legal_name, self.document_title)


@receiver(post_save, sender=StudentIdentificationDocument, dispatch_uid="student_verification_ready")
def student_verification_ready(sender, instance, **kwargs):
    student = instance.student
    if not student.verification_ready_on:
        total_verification_documents = StudentIdentificationDocument.objects.filter(student=student,
            verification_required=True)
        ready_documents = total_verification_documents.exclude(document='')
        if total_verification_documents.count() == ready_documents.count():
            student.verification_ready_on = timezone.now()
            student.save()
            dispatch_student_verification_email(student)

class Course(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='', help_text='Home page description of the course')
    enforce_minimum_time = models.BooleanField(default=False,
 		help_text='Does the student have to spend a certain amount of time to complete?')
    minimum_time_seconds = models.BigIntegerField(default=settings.MINIMUM_COURSE_SECONDS_DEFAULT,
 		help_text='Minimum time a student has to spend reading for a course to be considered complete')
    maximum_idle_time_seconds = models.BigIntegerField(default=settings.MAX_COURSE_IDLE_TIME_SECONDS,
 		help_text='Maximum time spent with no inputs before user is considered AFK')
    published = models.BooleanField(default=False, help_text='Course is ready to appear on the home page')
    pages_require_signature = models.BooleanField(default=False,
        help_text='Each page will require the student sign that they viewed the page')
    page_signature_description = models.TextField(default='Your full name',
        help_text='If pages require signature, this field will describe the signature the student enters')

    def continue_url(self, student):
        try:
            instance = CourseViewInstance.objects.get(course=self, student=student)
        except CourseViewInstance.DoesNotExist:
            return ""
        pages_viewed = CoursePageViewInstance.objects.filter(course_view_instance=instance)
        if pages_viewed:
            return pages_viewed.latest('created').url
        return ""

    def url_recent_history(self, student):
        try:
            instance = CourseViewInstance.objects.get(course=self, student=student)
        except CourseViewInstance.DoesNotExist:
            return []
        # get pages ordered by created
        # distinct queries by created are a lot harder than you think
        # keep the history short because we need python to calc distinct urls
        # if someone could figure out how to get the db to do the lifting here
        # please replace this
        pages_viewed = CoursePageViewInstance.objects.filter(
            course_view_instance=instance).order_by('-created')
        # need this count for performance if setting gets high 
        # or for low page instances with high views
        unique_url_count = CoursePageViewInstance.objects.filter(
            course_view_instance=instance).distinct('url').count()

        break_length = min(unique_url_count, settings.LEFT_NAV_HISTORY_MAX)
        return_list = []
        used_urls = []
        for page_viewed in pages_viewed:
            if len(return_list) >= break_length:
                break
            if page_viewed.url not in used_urls:
                used_urls.append(page_viewed.url)
                return_list.append(page_viewed.as_dict)

        return return_list

    @property
    def minimum_time(self):
        return human_time_duration(self.minimum_time_seconds)

    @property
    def course_pages_ordered(self):
        return self.course_pages.order_by('page_number')

    @property
    def course_tests_ordered(self):
        return self.course_tests.order_by('order')
    

    def __str__(self):
        return self.name

class CoursePage(BaseModel):
    course = models.ForeignKey(Course, null=True, on_delete=models.CASCADE,
        related_name='course_pages')
    page_number = models.IntegerField(default=1, help_text='Order of the page')
    page_title = models.CharField(max_length=200, help_text='Title of the page')
    page_contents = models.TextField(default="", help_text=mark_safe('''
     	The contents of your page. Regular paragraphs will work as expected
     	However, this is interpreted in markdown, so you can add extra styling<br/>
     	<a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">
        Click Here for a Markdown Cheat Sheet</a>
     	''')
    )

    objects = CoursePageManager()

    @property
    def course_url(self):
        if self.guid:
            return reverse('course_page', kwargs={'page_guid':self.guid})
        return None


    def __str__(self):
        return '%s %s %s' % (self.course.name, self.page_number, self.page_title)

class CoursePageMedia(BaseModel):
    course_page = models.ForeignKey(CoursePage, null=False, on_delete=models.CASCADE,
        related_name='page_media')
    file = models.FileField(upload_to='pagemedia/%Y/%m/%d/')

class CourseViewInstance(BaseModel):
    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE,
        related_name='course_view_instances')
    course = models.ForeignKey(Course, null=True, on_delete=models.CASCADE,
        related_name='course_view_instances')
    course_view_start = models.DateTimeField(null=True)
    course_view_stop = models.DateTimeField(null=True)
    total_seconds_spent = models.BigIntegerField(default=0)
    pages_require_signature = models.BooleanField(default=False)
    page_signature_description = models.TextField(default='', blank=True)
    student_course_signature_value = models.CharField(max_length=200, blank=True, null=True)
    first_page_view = models.ForeignKey('CoursePageViewInstance', null=True, related_name="+",
        on_delete=models.CASCADE)
    last_page_view = models.ForeignKey('CoursePageViewInstance', null=True, related_name="+",
        on_delete=models.CASCADE)

    @property
    def enforce_minimum_time(self):
        return self.course.enforce_minimum_time

    @property
    def read_time_remaining_seconds(self):
        return max((self.course.minimum_time_seconds - self.total_seconds_spent),0)

    def calculate_time_spent(self):
        time_spent_query = self.course_page_view_instances.aggregate(Sum('total_seconds_spent'))
        self.total_seconds_spent = time_spent_query['total_seconds_spent__sum']
        self.save()
        return self.total_seconds_spent

    class Meta:
        unique_together = ('student', 'course',)

    def __str__(self):
        return '%s, %s' % (self.student.full_legal_name, self.course)

class CoursePageViewInstance(BaseModel):
    url = models.TextField(blank=True, default='')
    course_view_instance = models.ForeignKey(CourseViewInstance, null=True, on_delete=models.CASCADE,
        related_name='course_page_view_instances')
    page_view_start = models.DateTimeField(null=True)
    page_view_stop = models.DateTimeField(null=True)
    total_seconds_spent = models.BigIntegerField(default=0)
    course_page = models.ForeignKey(CoursePage, null=True, on_delete=models.CASCADE,
        related_name='+')
    course_test = models.ForeignKey('CourseTest', null=True, on_delete=models.CASCADE,
        related_name='+')
    course_test_question = models.ForeignKey('MultipleChoiceTestQuestion',
        null=True, on_delete=models.CASCADE, related_name="+")
    page_signature = models.CharField(max_length=200, blank=True, null=True)


    @property
    def as_dict(self):
        d = {
        'url':self.url,
        'course_name':self.course_view_instance.course.name,
        'title': 'Uncategorized Bookmark',
        }
        if self.course_page:
            d['title'] = self.course_page.page_title
        elif self.course_test_question:
            d['title'] = '%s Test #%s - Question' % (
                d['course_name'],
                self.course_test_question.course_test.order
            )
        elif self.course_test:
            d['title'] = '%s Test %s' % (
                d['course_name'],
                self.course_test.order
            )

        return d

@receiver(post_save, sender=CoursePageViewInstance, dispatch_uid="update_total_course_time")
def update_total_course_time(sender, instance, **kwargs):
    if instance.total_seconds_spent:
        instance.course_view_instance.calculate_time_spent()

class CourseTest(BaseModel):
    course = models.ForeignKey(Course, null=True, on_delete=models.CASCADE,
        related_name='course_tests')
    order = models.IntegerField(default=1)
    max_number_of_question = models.IntegerField(default=0,
        help_text='maximum number of questions to generate. 0 generates all available questions once.')
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
    allow_practice_tests = models.BooleanField(default=True, help_text='Turn practice tests on or off')
    only_practice_test = models.BooleanField(default=False, help_text='When turned on only test only counts for practice')
    maximum_practice_tests = models.IntegerField(default=0, help_text='''
 		Maximum number of practice tests. 0 is infinite. If you want 0 tests uncheck allow practice tests
 	''')

    def __str__(self):
        return '%s %s' %(self.course.name, self.order)

class MultipleChoiceAnswer(BaseModel):
    value = models.CharField(max_length=300, help_text='What shows up on the multiple choice answer')
    # used for random generation ordering
    # combo a and b or other combos needs design
    is_all_of_the_above = models.BooleanField(default=False, help_text='Does this answer mean all of the above?')
    is_none_of_the_above = models.BooleanField(default=False, help_text='Does this answer mean none of the above?')
    # random generation define smaller set of questions for live tests or practice
    is_live_only = models.BooleanField(default=False, help_text='This question is only for live tests')
    is_practice_only = models.BooleanField(default=False, help_text='This question is only for practice tests')

    def __str__(self):
        return self.value

class MultipleChoiceTestQuestion(BaseModel):
    course_test = models.ForeignKey(CourseTest, null=True, on_delete=models.CASCADE,
        related_name='multiple_choice_test_questions')
    question_contents = models.TextField(default='', help_text='what the question will say')
    correct_multiple_choice_answer = models.ForeignKey(MultipleChoiceAnswer, null=True,
        on_delete=models.CASCADE, related_name='multiple_choice_test_questions')
    other_multiple_choice_answers = models.ManyToManyField(MultipleChoiceAnswer, related_name='course_tests',
        help_text='List of potential answers to appear in random generation')
    multiple_choice_answer_length = models.IntegerField(default=settings.DEFAULT_MULTIPLE_CHOICE_LENGTH,
        help_text = 'Total number of answers that will appear in the questions generated')

    def __str__(self):
        return self.question_contents

class CourseTestInstance(BaseModel):
    is_practice = models.BooleanField(default=False)
    course_test = models.ForeignKey(CourseTest, null=True, on_delete=models.CASCADE,
        related_name='course_test_instances')
    student = models.ForeignKey(Student, null=True, on_delete=models.CASCADE,
        related_name='course_test_instances')
    test_started_on = models.DateTimeField(null=True)
    test_finished_on = models.DateTimeField(null=True)
    available_questions = models.ManyToManyField(MultipleChoiceTestQuestion, related_name='course_test_instances')    

class CourseTestQuestionInstance(BaseModel):
    course_test_instance = models.ForeignKey(CourseTestInstance, null=True, on_delete=models.CASCADE,
        related_name='course_test_question_instances')
    course_test_question = models.ForeignKey(MultipleChoiceTestQuestion, null=True, 
        on_delete=models.CASCADE, related_name='+')
    order = models.IntegerField(default=1)

class CourseTestQuestionAnswerOption(BaseModel):
    question_instance = models.ForeignKey(CourseTestQuestionInstance, null=True, on_delete=models.CASCADE,
        related_name='course_test_answer_option_instances')
    answer_option = models.ForeignKey(MultipleChoiceAnswer, null=True, on_delete=models.CASCADE,
        related_name='+')
    order = models.IntegerField(default=1)

class CourseTestQuestionAnswerInstance(BaseModel):
    question_instance = models.ForeignKey(CourseTestQuestionInstance, null=True, on_delete=models.CASCADE,
        related_name='course_test_answer_instances')
    answer_chosen = models.ForeignKey(MultipleChoiceAnswer, null=True, on_delete=models.CASCADE,
        related_name='course_test_answer_instances')
    answer_chosen_on = models.DateTimeField(null=True)

