from django.urls import include, path, re_path
from . import views
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^student_profile/$', views.student_home, name='student_home'),
    re_path(r'^student_document_upload/(?P<document_guid>[a-zA-Z0-9_-]+)/$',
        views.student_document_upload, name='student_document_upload'),
    re_path(r'^student_verification/(?P<student_guid>[a-zA-Z0-9_-]+)/$',
        views.student_verification, name='student_verification'),
    re_path(r'^student_dashboard/$', views.student_dashboard, name='student_dashboard'),

]
