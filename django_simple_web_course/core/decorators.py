from .models import Student
from django.conf import settings
from django.http import HttpResponseRedirect

def student_login_required(function):
    def wrapper(request, *args, **kw):
        user=request.user  
        if not user or not (user.id):
            return HttpResponseRedirect('/')
        student_id = request.session.get('student_id', None)
        if student_id is None:
            student = Student.objects.get_or_create_from_user(user=user)
            student_id = student.pk
            request.session['student_id'] = student_id
        request.student = Student.objects.get(pk=student_id)
        if request.student.is_verified or request.path == settings.LOGIN_REDIRECT_URL:
            return function(request, *args, **kw)

        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    return wrapper
