from .models import Student
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages

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
