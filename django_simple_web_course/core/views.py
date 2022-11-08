from django.shortcuts import render
from .decorators import student_login_required
from .forms import StudentProfileForm, StudentIdentificationDocumentForm, StudentVerificationForm
from .models import (StudentIdentificationDocument, Student, Course, CoursePage, CoursePageMedia,
    CoursePageMedia, CourseViewInstance, CoursePageViewInstance, CourseTest, MultipleChoiceAnswer,
    MultipleChoiceTestQuestion, CourseTestInstance, CourseTestAnswerInstance)
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .email_dispatchers import email_student_reverification, email_student_verification_complete
import json

# views should be class based, for dev speed writing functions to convert later

def index(request):
    return render(request, 'index.html', {})

def send_form_error_messages(form, request):
    error_dict = json.loads(form.errors.as_json())
    for error_field, error_list in error_dict.items():
        for error in error_list:
            messages.add_message(request, messages.ERROR,
            '%s: %s' % (error_field.replace('_', ' ').capitalize(),
                error['message']))

@staff_member_required
def student_verification(request, student_guid=None):
    try:
        student = Student.objects.get(guid=student_guid)
        docs = StudentIdentificationDocument.objects.filter(student=student,
            verification_required=True)
    except:
        raise Http404
    form = StudentVerificationForm()
    if request.method == 'POST':
        form = StudentVerificationForm(request.POST)
        if form.is_valid():
            # form is approved, verify the student and docs
            if form['verified'].value() == 'A':
                for doc in docs:
                    doc.verified = True
                    doc.save()
                student.verified_on = timezone.now()
                student.verified_by = request.user
                student.save()
                email_student_verification_complete(student, form['student_note'].value())
            # form is rejected, reset docs, unverify student, notify student
            if form['verified'].value() == 'R':
                for doc in docs:
                    doc.verified = False
                    doc.document = ''
                    doc.save()
                student.verified_on = None
                student.verified_by = None
                student.verification_ready_on = None
                student.save()
                email_student_reverification(student, form['student_note'].value())
            return HttpResponseRedirect(student.admin_change_url)

    return render(request, 'student_verification.html',{
        'student':student,
        'docs':docs,
        'form': form,

    })


@student_login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html', {
        'student':request.student,
        'available_courses': Course.objects.filter(published=True),
    })

@student_login_required
def course_home_view(request, course_guid=None):
    if not course_guid:
        raise Http404

    return render(request, 'course_home.html', {
        'student': request.student,
        'course': Course.objects.get(guid=course_guid),
    })

@student_login_required
def course_page_view(request, page_guid=None):
    if not page_guid:
        raise Http404
    course_page = CoursePage.objects.get(guid=page_guid)

    return render(request, 'course_page.html', {
        'student':request.student,
        'page': page,
    })

@student_login_required
def course_practice_test_home_view(request, test_guid=None):
    if not test_guid:
        raise Http404
    course_test = CourseTest.objects.get(guid=test_guid)

    return render(request, 'course_practice_test_home.html', {
        'student':request.student,
        'course_test': course_test,
    })


@student_login_required
def course_practice_test_question_view(request, question_guid=None):
    if not question_guid:
        raise Http404
    course_test_question = MultipleChoiceTestQuestion.objects.get(guid=question_guid)

    return render(request, 'course_practice_test_question.html', {
        'student':request.student,
        'course_test_question': course_test_question,
    })

@student_login_required
def course_test_home_view(request, test_guid=None):
    if not test_guid:
        raise Http404
    course_test = CourseTest.objects.get(guid=test_guid)

    return render(request, 'course_test_home.html', {
        'student':request.student,
        'course_test': course_test,
    })


@student_login_required
def course_test_question_view(request, question_guid=None):
    if not question_guid:
        raise Http404
    course_test_question = MultipleChoiceTestQuestion.objects.get(guid=question_guid)

    return render(request, 'course_test_question.html', {
        'student':request.student,
        'course_test_question': course_test_question,
    })

@student_login_required
def course_complete_view(request, course_guid=None):
    if not course_guid:
        raise Http404
    course = Course.objects.get(guid=course_guid)

    return render(request, 'course_complete.html', {
        'student': request.student,
        'course': course,
    })


@student_login_required
def student_home(request):
    if request.method =="POST":
        form = StudentProfileForm(request.POST, instance=request.student)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Profile Changes Saved.')
        else:
            send_form_error_messages(form, request)

        return render(request, 'student_home.html', {
            'form':form,
            'student':request.student,
            'document_forms': request.student.document_forms
        })

    form = StudentProfileForm(instance=request.student)
    return render(request, 'student_home.html', {
        'form': form,
        'student':request.student,
        'document_forms': request.student.document_forms
    })

@login_required
def student_document_upload(request, document_guid=None):
    # can't look up a doc if there's no guid
    if not document_guid:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    if request.method == 'POST':
        doc = StudentIdentificationDocument.objects.get(guid=document_guid)
        if doc.student.user.pk != request.user.pk:
            # by some miracle you guessed someone else's guid. 404
            raise Http404
        form = StudentIdentificationDocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                'Successful upload of %s' % doc.document_title)
        else:
            send_form_error_messages(form, request)

    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
