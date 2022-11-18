from django.contrib import admin
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
CourseViewInstance, CoursePageViewInstance, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion,
 CoursePageMedia, CourseTestInstance, CourseTestQuestionInstance, CourseTestQuestionAnswerOption)
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class StudentIdentificationDocumentInline(admin.TabularInline):
    model = StudentIdentificationDocument

class StudentAdmin(admin.ModelAdmin):
    list_display = ('guid', 'prefix', 'first_name', 'middle_name', 'last_name',
        'suffix', 'email_address', 'primary_phone_number', 'verification_ready_on',
        'verified_on', 'verified_by', 'get_verification_link')

    inlines = (StudentIdentificationDocumentInline,)

    def get_verification_link(self, obj):
        return obj.verification_link
    get_verification_link.admin_order_field = 'verification_ready_on'

admin.site.register(Student, StudentAdmin)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'enforce_minimum_time')

admin.site.register(Course, CourseAdmin)

class CoursePageMediaInline(admin.TabularInline):
    model = CoursePageMedia

class CoursePageAdmin(admin.ModelAdmin):
    list_display = ('course', 'page_number', 'page_title', 'page_contents')
    inlines = (CoursePageMediaInline, )

admin.site.register(CoursePage, CoursePageAdmin)

class CourseTestAdmin(admin.ModelAdmin):
    list_display = ('course', 'test_is_timed', 'maximum_time_seconds', 'is_course_fixed_answer_length',
        'course_fixed_answer_length', 'order', 'allow_practice_tests')

admin.site.register(CourseTest, CourseTestAdmin)

class MultipleChoiceAnswerAdmin(admin.ModelAdmin):
    list_display = ('value', )

admin.site.register(MultipleChoiceAnswer, MultipleChoiceAnswerAdmin)

class MultipleChoiceOtherAnswerInline(admin.TabularInline):
    model = MultipleChoiceTestQuestion.other_multiple_choice_answers.through
    verbose_name = "Wrong answer option"
    verbose_name_plural = "Wrong answer options"

class MultipleChoiceTestQuestionAdmin(admin.ModelAdmin):
    list_display = ('course_test', 'question_contents', 'correct_multiple_choice_answer',
        'multiple_choice_answer_length', )
    fields = ('course_test', 'question_contents', 'question_post_answer_comments',
        'correct_multiple_choice_answer', 'multiple_choice_answer_length')

    inlines = (MultipleChoiceOtherAnswerInline, )

admin.site.register(MultipleChoiceTestQuestion, MultipleChoiceTestQuestionAdmin)

class CoursePageViewInstanceAdmin(admin.ModelAdmin):
    list_display = ('url', 'course_view_instance', 'page_view_start', 'page_view_stop', 'total_seconds_spent')

admin.site.register(CoursePageViewInstance,CoursePageViewInstanceAdmin)

admin.site.register(CourseTestInstance, admin.ModelAdmin)
admin.site.register(CourseTestQuestionInstance, admin.ModelAdmin)
admin.site.register(CourseTestQuestionAnswerOption, admin.ModelAdmin)
