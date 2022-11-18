from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.safestring import mark_safe
from django.db.models import F, Q
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
    def model_class(self):
        return type(self)

    @property
    def get_manager(self):
        return self.model_class._default_manager

    @property
    def DoesNotExist(self):
        return self.model_class.DoesNotExist

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

    student = models.ForeignKey('Student', null=False, on_delete=models.CASCADE,
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
    practice_counts_for_time = models.BooleanField(default=True, 
        help_text='Time spent on practice tests counts towards the minimum time')
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
    def live_tests(self):
        return self.course_tests.filter(only_practice_test=False)

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
    course = models.ForeignKey('Course', null=True, on_delete=models.CASCADE,
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

    @property
    def nav_page_split(self):
        course_pages = self.course.course_pages.order_by('page_number')
        total_pages = course_pages.count()
        if  total_pages == 0:
            return ''

        guid_ordered_list = [ page.guid for page in course_pages]
        page_index = guid_ordered_list.index(self.guid)
        if total_pages <= 10:
            page_indexing_obj = set(range(1, total_pages + 1))
        else:
            page_indexing_obj = (set(range(1, 4))
                     | set(range(max(1, page_index - 1), min(page_index + 4, total_pages + 1)))
                     | set(range(total_pages - 2, total_pages + 1)))

        def display_at_index(index, guid_list, target_index):
            tag_url = reverse('course_page', kwargs={'page_guid':guid_list[index-1]})
            inner_tag = str(index) if index != target_index else '[ %s ]' % index
            return '<div class="col"><a href="%s">%s</a></div>' % (tag_url, inner_tag)

        # Display pages in order with ellipses
        def display():
            last_page = 0
            for p in sorted(page_indexing_obj):
                if p != last_page + 1: yield '<div class="col">...</div>'
                yield display_at_index(p, guid_ordered_list, page_index+1)
                last_page = p
        display_columns = ' '.join(display())
        return mark_safe('<div class="row page-navigation-bar">%s</div>' % display_columns)

    @property
    def course_url(self):
        if self.guid:
            return reverse('course_page', kwargs={'page_guid':self.guid})
        return None


    def __str__(self):
        return '%s %s %s' % (self.course.name, self.page_number, self.page_title)

class CoursePageMedia(BaseModel):
    course_page = models.ForeignKey('CoursePage', null=False, on_delete=models.CASCADE,
        related_name='page_media')
    file = models.FileField(upload_to='pagemedia/%Y/%m/%d/')

class CourseViewInstance(BaseModel):
    student = models.ForeignKey('Student', null=True, on_delete=models.CASCADE,
        related_name='course_view_instances')
    course = models.ForeignKey('Course', null=True, on_delete=models.CASCADE,
        related_name='course_view_instances')
    course_view_start = models.DateTimeField(null=True)
    course_view_stop = models.DateTimeField(null=True)
    total_seconds_spent = models.BigIntegerField(default=0)
    pages_require_signature = models.BooleanField(default=False)
    page_signature_description = models.TextField(default='', blank=True)
    student_course_signature_value = models.CharField(max_length=200, blank=True, null=True)

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
    course_view_instance = models.ForeignKey('CourseViewInstance', null=True, on_delete=models.CASCADE,
        related_name='course_page_view_instances')
    page_view_start = models.DateTimeField(null=True)
    page_view_stop = models.DateTimeField(null=True)
    total_seconds_spent = models.BigIntegerField(default=0)
    course_page = models.ForeignKey('CoursePage', null=True, on_delete=models.CASCADE,
        related_name='+')
    course_test = models.ForeignKey('CourseTest', null=True, on_delete=models.CASCADE,
        related_name='+')
    course_test_question = models.ForeignKey('MultipleChoiceTestQuestion',
        null=True, on_delete=models.CASCADE, related_name="+")
    course_test_instance = models.ForeignKey('CourseTestInstance', null=True, on_delete=models.CASCADE,
        related_name='course_page_view_instances')
    page_signature = models.CharField(max_length=200, blank=True, null=True)
    student = models.ForeignKey('Student', null=True, on_delete=models.CASCADE,
        related_name='course_page_view_instances')

    @property
    def credit_page_view_time(self):
        # function not finished paused to fix arch problem
        if self.course_page:
            return True
        if self.course_view_instance.course.practice_counts_for_time:
            test_obj = self.course_test
            if self.course_test_question:
                test_obj = self.course_test_question.course_test
            if test_obj and test_obj:
                return True
        return False


    @property
    def as_dict(self):
        question_number = ''
        if self.course_test_question and self.course_test_instance:
            try:
                # if this fails do nothing is fine
                question_number = self.course_test_instance.course_test_question_instances.get(
                    course_test_question=self.course_test_question).order
            except Exception as e:
                print(e)

        d = {
        'url':self.url,
        'course_name':self.course_view_instance.course.name,
        'title': 'Uncategorized Bookmark',
        }
        if self.course_page:
            d['title'] = self.course_page.page_title
        elif self.course_test_question:
            d['title'] = 'Test #%s - Question %s' % (
                self.course_test_question.course_test.order,
                question_number
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

class CourseTestInstance(BaseModel):
    is_practice = models.BooleanField(default=False)
    # build a retake of live test mechanic later
    # if retake is linked, the newer test will be the foreign key
    retake = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    course_test = models.ForeignKey('CourseTest', null=True, on_delete=models.CASCADE,
        related_name='course_test_instances')
    student = models.ForeignKey('Student', null=True, on_delete=models.CASCADE,
        related_name='course_test_instances')
    test_started_on = models.DateTimeField(null=True)
    test_finished_on = models.DateTimeField(null=True)
    available_questions = models.ManyToManyField('MultipleChoiceTestQuestion', related_name='course_test_instances')    

    @property
    def passing_percentage(self):
        return self.course_test.passing_percentage

    @property
    def is_complete(self):
        if self.has_time_expired:
            return True
        if (not self.test_started_on) or (self.course_test.number_of_available_questions > 
            self.course_test_question_instances.count()):
            return False
        complete = self.course_test_question_instances.count() == self.course_test_question_instances.filter(
            course_test_answer_instance__isnull=False).count()
        if complete and not self.test_finished_on:
            self.test_finished_on = timezone.now()
            self.save()
        return complete

    @property
    def has_time_expired(self):
        if self.test_finished_on:
            return True
        if not self.course_test.test_is_timed:
            return False
        if ((self.test_started_on) and (self.test_started_on + timezone.timedelta(
            seconds=self.maximum_time_seconds) < timezone.now())):
            self.test_finished_on = timezone.now()
            self.save()
            return True
        return False


    @property
    def maximum_time_seconds(self):
        return self.course_test.maximum_time_seconds

    @property
    def number_of_correct_answers(self):
        return self.course_test_question_instances.filter(
            course_test_question__correct_multiple_choice_answer=F('course_test_answer_instance__answer_chosen')
            ).count()

    @property
    def total_number_of_questions(self):
        return self.course_test_question_instances.count()

    @property
    def question_instances(self):
        return self.course_test_question_instances.order_by('order')
    

    @property
    def test_score_percent(self):
        return float('{0:.2f}'.format(
            self.number_of_correct_answers / self.total_number_of_questions * 100))

    @property
    def test_passed(self):
        return self.test_score_percent >= self.passing_percentage

class CourseTestQuestionAnswerOption(BaseModel):
    question_instance = models.ForeignKey('CourseTestQuestionInstance', null=True, on_delete=models.CASCADE,
        related_name='course_test_answer_option_instances')
    answer_option = models.ForeignKey('MultipleChoiceAnswer', null=True, on_delete=models.CASCADE,
        related_name='+')
    order = models.IntegerField(default=1)

    @property
    def value(self):
        return self.answer_option.value

class CourseTestQuestionAnswerInstance(BaseModel):
    question_instance = models.OneToOneField('CourseTestQuestionInstance', null=True, on_delete=models.CASCADE,
        related_name='course_test_answer_instance')
    answer_chosen = models.ForeignKey('MultipleChoiceAnswer', null=True, on_delete=models.CASCADE,
        related_name='course_test_answer_instances')
    answer_chosen_on = models.DateTimeField(null=True)

    @property
    def value(self):
        return self.answer_chosen.value

    @property
    def is_correct(self):
        return self.answer_chosen == self.question_instance.correct_multiple_choice_answer

class CourseTestQuestionInstance(BaseModel):
    course_test_instance = models.ForeignKey('CourseTestInstance', null=True, on_delete=models.CASCADE,
        related_name='course_test_question_instances')
    course_test_question = models.ForeignKey('MultipleChoiceTestQuestion', null=True, 
        on_delete=models.CASCADE, related_name='+')
    order = models.IntegerField(default=1)

    @property
    def answer_instance(self):
        try:
            return self.course_test_answer_instance
        except CourseTestQuestionAnswerInstance.DoesNotExist:
            return None

    def choose_answer(self, answer_chosen):
        # clock is up, deny the answer
        if self.course_test_instance.has_time_expired:
            return None
        answer_instance = CourseTestQuestionAnswerInstance.objects.create(
            question_instance=self,
            answer_chosen=answer_chosen,
            answer_chosen_on=timezone.now()
        )
        answer_instance.save()
        return answer_instance

    @property
    def url(self):
        if self.course_test_instance.is_practice:
            return reverse('course_practice_test_question', 
                kwargs={'question_instance_guid':self.guid})
        return reverse('course_test_question', 
            kwargs={'question_instance_guid':self.guid})

    @property
    def question_form(self):
        from core.forms import TestQuestionInstanceForm
        return TestQuestionInstanceForm(question_instance=self)

    @property
    def answer_options(self):
        return self.course_test_answer_option_instances.order_by('order')

    @property
    def question_contents(self):
        return self.course_test_question.question_contents

    @property
    def question_post_answer_comments(self):
        return self.course_test_question.question_post_answer_comments

    @property
    def correct_multiple_choice_answer(self):
        return self.course_test_question.correct_multiple_choice_answer

    @property
    def other_multiple_choice_answers(self):
        return self.course_test_question.other_multiple_choice_answers.order_by('-created')

    @property
    def course_test(self):
        return self.course_test_instance.course_test

    def create_answer_options(self):
        question_obj = self.course_test_question
        answer_length = question_obj.calculated_answer_length
        # no answers in the pool, can't create
        if answer_length <= 1:
            return None

        incorrect_answer_indexes_added = []
        order_keys_used = []
        # this structure exists to help random index placement
        answer_order_key = {i:None for i in range(0,answer_length)}
        correct_answer_placement_index = randrange(0, answer_length)
        order_keys_used.append(correct_answer_placement_index)
        answer_order_key[correct_answer_placement_index] = question_obj.correct_multiple_choice_answer
        
        wrong_answers = question_obj.other_multiple_choice_answers.order_by('-created')
        while len(incorrect_answer_indexes_added) < answer_length -1:
            # get an unused order key to place an answer
            random_order_key = randrange(0, answer_length)
            while random_order_key in order_keys_used:
                random_order_key = randrange(0, answer_length)
            order_keys_used.append(random_order_key)
            # get an unused wrong answer index
            wrong_answer_index = randrange(0, wrong_answers.count())
            while wrong_answer_index in incorrect_answer_indexes_added:
                 wrong_answer_index = randrange(0, wrong_answers.count())
            incorrect_answer_indexes_added.append(wrong_answer_index)
            # make structure assignment
            answer_order_key[random_order_key] = wrong_answers[wrong_answer_index]
        # now that we've filled the dict create a list comprehension
        # excluding none of the above and all the above answers

        answer_list = [
            answer_order_key[key] for key in range(0,answer_length)
            if (not(answer_order_key[key].is_all_of_the_above) 
                and not(answer_order_key[key].is_none_of_the_above))
        ]
        # now we add a list only including none or all the aboves
        none_all_list = [
            answer_order_key[key] for key in range(0,answer_length)
            if (answer_order_key[key].is_all_of_the_above
                or answer_order_key[key].is_none_of_the_above)
        ]
        # we finally have all answers ordered, create the list
        final_list = answer_list + none_all_list
        for order, answer in enumerate(final_list):
            new_option = CourseTestQuestionAnswerOption.objects.create(
                question_instance=self,
                answer_option=answer,
                order=order
            )
            new_option.save()

        return final_list

    @property
    def previous_instance_url(self):
        try:
            instance = self.get_manager.get(course_test_instance=self.course_test_instance, 
                order=self.order-1)
            if self.course_test_instance.is_practice:
                return reverse(
                    'course_practice_test_question', kwargs={'question_instance_guid':instance.guid})
            return reverse('course_test_question', kwargs={'question_instance_guid':instance.guid})
        except self.DoesNotExist:
            return ''

    @property
    def next_instance_url(self):
        try:
            instance = self.get_manager.get(course_test_instance=self.course_test_instance, 
                order=self.order+1)
            if self.course_test_instance.is_practice:
                return reverse(
                    'course_practice_test_question', kwargs={'question_instance_guid':instance.guid})
            return reverse('course_test_question', kwargs={'question_instance_guid':instance.guid})
        except self.DoesNotExist:
            return ''

class CourseTest(BaseModel):
    course = models.ForeignKey('Course', null=True, on_delete=models.CASCADE,
        related_name='course_tests')
    order = models.IntegerField(default=1)
    max_number_of_questions = models.IntegerField(default=0,
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
 		help_text='''
        The fixed length of the answers if "Is course fixed answer length" is checked.
        0 generates all questions
        ''')
    allow_practice_tests = models.BooleanField(default=True, help_text='Turn practice tests on or off')
    only_practice_test = models.BooleanField(default=False, 
        help_text='When turned on only test only counts for practice')
    passing_percentage = models.IntegerField(default=60, help_text='The minimum percentage needed to pass')

    @property
    def number_of_available_questions(self):
        # default max is the number of key relations
        max_number_of_questions = self.multiple_choice_test_questions.count()
        # 0 means length of test questions
        if self.max_number_of_questions:
            max_number_of_questions = min(
                max_number_of_questions, self.max_number_of_questions)
        return max_number_of_questions

    @property
    def time_limit(self):
        return human_time_duration(self.maximum_time_seconds)

    def get_or_generate_test_instance_for_student(self, student, is_practice=False):
        from .models import CourseTestInstance, CourseTestQuestionInstance
        #look for an existing active test and return if relevant
        # we generate new practice tests after old ones are finished
        if is_practice:
            active_tests = self.course_test_instances.filter(student=student, 
                test_finished_on__isnull=True, is_practice=is_practice)
        # live test. Cannot have a retake marked, return completed tests as well
        # return of a completed test will mean inability to take a new one
        else:
            active_tests = self.course_test_instances.filter(student=student,
                is_practice=is_practice, retake__isnull=True)
        if active_tests.count() > 0:
            return active_tests[0]

        # no active tests found, generate one
        number_of_available_questions = self.number_of_available_questions
        # we can only generate if we have questions
        if number_of_available_questions > 0:
            new_test_instance = CourseTestInstance.objects.create(is_practice=is_practice,
                course_test=self, student=student)
            new_test_instance.save()
            # generate the questions
            
            available_questions = self.multiple_choice_test_questions.order_by('-created')
            indexes_added = []
            while len(indexes_added) < number_of_available_questions:
                random_index = randrange(0, number_of_available_questions)
                while random_index in indexes_added:
                    random_index = randrange(0, number_of_available_questions)
                indexes_added.append(random_index)
                random_question = available_questions[random_index]
                new_question = CourseTestQuestionInstance.objects.create(
                    course_test_instance=new_test_instance,
                    course_test_question=random_question,
                    order=len(indexes_added))
                new_question.save()
                new_question.create_answer_options()

            return new_test_instance

        return None


    def __str__(self):
        return '%s %s' %(self.course.name, self.order)

class MultipleChoiceAnswer(BaseModel):
    value = models.CharField(max_length=300, help_text='What shows up on the multiple choice answer')
    # used for random generation ordering
    # combo a and b or other combos needs design
    is_all_of_the_above = models.BooleanField(default=False, help_text='Does this answer mean all of the above?')
    is_none_of_the_above = models.BooleanField(default=False, help_text='Does this answer mean none of the above?')

    def __str__(self):
        return self.value

class MultipleChoiceTestQuestion(BaseModel):
    course_test = models.ForeignKey('CourseTest', null=True, on_delete=models.CASCADE,
        related_name='multiple_choice_test_questions')
    question_contents = models.TextField(default='', help_text=mark_safe('''
        The contents of your question. Regular paragraphs will work as expected
        However, this is interpreted in markdown, so you can add extra styling<br/>
        <a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">
        Click Here for a Markdown Cheat Sheet</a>
        ''')
    )
    question_post_answer_comments = models.TextField(default='', help_text=mark_safe('''
        Educational comments that will show only after the question is answered.
        Regular paragraphs will work as expected
        However, this is interpreted in markdown, so you can add extra styling<br/>
        <a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">
        Click Here for a Markdown Cheat Sheet</a>
        ''')
    )
    correct_multiple_choice_answer = models.ForeignKey('MultipleChoiceAnswer', null=True,
        on_delete=models.CASCADE, related_name='multiple_choice_test_questions')
    other_multiple_choice_answers = models.ManyToManyField('MultipleChoiceAnswer', related_name='course_tests',
        help_text='List of potential answers to appear in random generation')
    multiple_choice_answer_length = models.IntegerField(default=settings.DEFAULT_MULTIPLE_CHOICE_LENGTH,
        help_text = 'Total number of answers that will appear in the questions generated. 0 generates all')

    @property
    def calculated_answer_length(self):
        # +1 for correct answer
        max_available = self.other_multiple_choice_answers.count() + 1
        if self.course_test.is_course_fixed_answer_length:
            if self.course_test.course_fixed_answer_length:
                return min(max_available, self.course_test.course_fixed_answer_length)
            return max_available
        if self.multiple_choice_answer_length:
            return min(max_available, self.multiple_choice_answer_length)
        return max_available

    def __str__(self):
        return self.question_contents



