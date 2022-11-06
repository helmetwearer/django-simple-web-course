from django.contrib import admin
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
CourseViewInstance, CoursePageViewInstance, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion,
CourseTestInstance, CourseTestAnswerInstance, CoursePageMedia)
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
    list_display = ('prefix', 'first_name', 'middle_name', 'last_name',
        'suffix', 'email_address', 'primary_phone_number')

    inlines = (StudentIdentificationDocumentInline,)

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
        'course_fixed_answer_length', 'order', 'allow_practice_tests', 'maximum_practice_tests')

admin.site.register(CourseTest, CourseTestAdmin)

class MultipleChoiceAnswerAdmin(admin.ModelAdmin):
    list_display = ('value', 'is_live_only', 'is_practice_only')

admin.site.register(MultipleChoiceAnswer, MultipleChoiceAnswerAdmin)

class MultipleChoiceOtherAnswerInline(admin.TabularInline):
    model = MultipleChoiceTestQuestion.other_multiple_choice_answers.through

class MultipleChoiceTestQuestionAdmin(admin.ModelAdmin):
    list_display = ('course_test', 'question_contents', 'correct_multiple_choice_answer',
        'multiple_choice_answer_length', )

    inlines = (MultipleChoiceOtherAnswerInline, )

admin.site.register(MultipleChoiceTestQuestion, MultipleChoiceTestQuestionAdmin)


