from django.urls import include, path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path(settings.LOGIN_REDIRECT_URL[1:], views.student_home, name='student_home'),
]
