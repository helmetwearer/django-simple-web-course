from django.shortcuts import render
from .decorators import student_login_required
from .forms import StudentProfileForm
from django.http import HttpResponseRedirect
from django.conf import settings

def index(request):
    return render(request, 'index.html', {})

@student_login_required
def student_home(request):
    if request.method =="POST":
        form = StudentProfileForm(request.POST, instance=request.student)
        if form.is_valid():
            form.save()
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
    if not document_slug:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
