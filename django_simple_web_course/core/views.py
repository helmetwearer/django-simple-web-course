from django.shortcuts import render
from .decorators import student_login_required
# Create your views here.

def index(request):
    return render(request, 'index.html', {})

@student_login_required
def student_home(request):
    return render(request, 'student_home.html', {})
