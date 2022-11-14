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
    re_path(r'^course_home/(?P<course_guid>[a-zA-Z0-9_-]+)/$',
        views.course_home_view, name='course_home'),
    re_path(r'^course_page/(?P<page_guid>[a-zA-Z0-9_-]+)/$',
        views.course_page_view, name='course_page'),
    re_path(r'^course_practice_test_home/(?P<test_guid>[a-zA-Z0-9_-]+)/$',
        views.course_practice_test_home_view, name='course_practice_test_home'),
    re_path(r'^course_practice_test_question/(?P<question_instance_guid>[a-zA-Z0-9_-]+)/$',
        views.course_practice_test_question_view, name='course_practice_test_question'),
    re_path(r'^course_test_home/(?P<test_guid>[a-zA-Z0-9_-]+)/$',
        views.course_test_home_view, name='course_test_home'),
    re_path(r'^course_test_question/(?P<question_instance_guid>[a-zA-Z0-9_-]+)/$',
        views.course_test_question_view, name='course_test_question'),
    re_path(r'^course_complete/(?P<course_guid>[a-zA-Z0-9_-]+)/$',
        views.course_complete_view, name='course_complete'),
]
