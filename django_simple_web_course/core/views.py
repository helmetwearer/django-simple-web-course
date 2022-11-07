from django.shortcuts import render
from .decorators import student_login_required
from .forms import StudentProfileForm, StudentIdentificationDocumentForm
from .models import StudentIdentificationDocument
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
import json

def index(request):
    return render(request, 'index.html', {})

def send_form_error_messages(form, request):
    error_dict = json.loads(form.errors.as_json())
    for error_field, error_list in error_dict.items():
        for error in error_list:
            messages.add_message(request, messages.ERROR,
            '%s: %s' % (error_field.replace('_', ' ').capitalize(),
                error['message']))

@student_login_required
def student_home(request, file_form=None):
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

@student_login_required
def student_document_upload(request, document_slug=None):
    # can't look up a doc if there's no slug
    if not document_slug:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    if request.method == 'POST':
        doc = StudentIdentificationDocument.objects.get(slug=document_slug)
        form = StudentIdentificationDocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                'Successful upload of %s' % doc.document_title)



    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
