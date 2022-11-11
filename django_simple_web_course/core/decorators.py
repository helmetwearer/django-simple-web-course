from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone


from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
    CoursePageMedia, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion,
    CourseViewInstance, CoursePageViewInstance)

def student_login_required(function):
    def wrapper(request, *args, **kwargs):
        user=request.user  
        if not user or not (user.id):
            return HttpResponseRedirect('/accounts/login')
        student_id = request.session.get('student_id', None)
        if student_id is None:
            student = Student.objects.get_or_create_from_user(user=user)
            student_id = str(student.guid)
            request.session['student_id'] = student_id
        request.student = Student.objects.get(guid=student_id)
        if request.student.is_verified:
            return function(request, *args, **kwargs)
        elif request.path != settings.LOGIN_REDIRECT_URL:
            if request.student.verification_ready_on:
                messages.add_message(request, messages.SUCCESS, '''
                    All of your verification documents have been uploaded. You will receive an email
                    when you account has been verified''')
            else:
                messages.add_message(request, messages.INFO, '''
                    Upload your verification documents in the forms below''')
        if request.path == settings.STUDENT_PROFILE_URL:
            return function(request, *args, **kwargs)
        return HttpResponseRedirect(settings.STUDENT_PROFILE_URL)
    return wrapper

def get_tracking_models(request, *args, **kwargs):
    student, course_obj, course_page, course_test, test_question = (None,
        None, None, None, None)
    
    student_id = request.session.get('student_id', None)
    if student_id:
        student = Student.objects.get(guid=student_id)
    else:
        student = Student.objects.get(user=request.user)

    if 'course_guid' in kwargs:
        course_obj = course.objects.get(guid=kwargs['course_guid'])
    if 'page_guid' in kwargs:
        course_page = CoursePage.objects.get(guid=kwargs['page_guid'])
    if 'test_guid' in kwargs:
        course_test = CourseTest.objects.get(guid=kwargs['test_guid'])
    if 'question_guid' in kwargs:
        test_question = MultipleChoiceTestQuestion.objects.get(guid=kwargs['question_guid'])
    if course_obj is None and course_page:
        course_obj = course_page.course
    if course_obj is None and course_test:
        course_obj = course_test.course
    if course_obj is None and test_question:
        course_obj = test_question.course_test.course

    return (student, course_obj, course_page, course_test, test_question)

def get_or_create_course_view_instance(student, course_obj):
    try:
        course_view_instance = CourseViewInstance.objects.get(student=student, course=course_obj)
    except CourseViewInstance.DoesNotExist:
        course_view_instance = CourseViewInstance.objects.create(student=student, course=course_obj,
            course_view_start=timezone.now(), pages_require_signature=course_obj.pages_require_signature,
            page_signature_description=course_obj.page_signature_description)
        course_view_instance.save()
        return get_or_create_course_view_instance(student, course_obj)

    return course_view_instance

def create_page_view_instance(request, student, course_obj, course_page, course_test,
 test_question, course_view_instance):
    page_view_instance = CoursePageViewInstance.objects.create(url=request.path, 
        course_view_instance=course_view_instance, page_view_start=timezone.now(), 
        course_page=course_page, course_test=course_test, 
        course_test_question=test_question)
    page_view_instance.save()
    # add page view guid to session so middleware can mark it complete
    # even outside of page tracking
    request.session['page_view_instance_guid'] = str(page_view_instance.guid)

    return page_view_instance


def page_tracking_enabled(function):
    def wrapper(request, *args, **kwargs):
        student, course_obj, course_page, course_test, test_question = get_tracking_models(request, *args, **kwargs)
        course_view_instance = get_or_create_course_view_instance(student, course_obj)
        page_view_instance = create_page_view_instance(request, student, course_obj, course_page,
            course_test, test_question, course_view_instance)

        return function(request, *args, **kwargs)

    return wrapper