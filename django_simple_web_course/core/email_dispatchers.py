from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from users.models import User
from django.conf import settings


def send_template_mail(subject, template_name, context, to_list):
    context['url_prepend'] = 'http://%s' % Site.objects.get_current().domain
    html_content = render_to_string(template_name, context=context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content,
        settings.DEFAULT_FROM_EMAIL, to_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# dispatch email to staff student needs to be verified
def dispatch_student_verification_email(student):
    send_template_mail(
        'New student verification: %s' % student.full_legal_name,
        'system_mail/student_verification_email.html',
        {'student':student},
        [ user.email for user in User.objects.filter(is_staff=True) ]
    )

def email_student_reverification(student, admin_note):
    send_template_mail(
        '%s, your verification documents need resubmitting' % student.first_name,
        'system_mail/student_reverification_email.html',
        {'student':student, 'admin_note':admin_note},
        list(set([student.email_address, student.user.email]))
    )

def email_student_verification_complete(student, admin_note):
    send_template_mail(
        '%s, your verification documents were approved!' % student.first_name,
        'system_mail/verification_complete_email.html',
        {'student':student, 'admin_note':admin_note},
        list(set([student.email_address, student.user.email]))
    )

def dispatch_test_retake_email(course_test_instance):
    student = course_test_instance.student
    send_template_mail(
        '%s has requested a retake for %s Test %s' %(student.first_name, 
            course_test_instance.course, course_test_instance.order),
        'system_mail/retake_request.html',
        {'student':student, 'instance':course_test_instance},
        [ user.email for user in User.objects.filter(is_staff=True) ]
    )

def dispatch_test_retake_approved_email(course_test_instance, admin_note):
    student = course_test_instance.student
    send_template_mail(
        '%s, your retake request was approved!' % student.first_name,
        'system_mail/retake_approved.html',
        {'student':student, 'instance':course_test_instance, 'admin_note':admin_note},
        list(set([student.email_address, student.user.email]))
    )

def dispatch_test_retake_rejected_email(course_test_instance, admin_note):
    student = course_test_instance.student
    send_template_mail(
        '%s, your retake request was denied' % student.first_name,
        'system_mail/retake_rejected.html',
        {'student':student, 'instance':course_test_instance, 'admin_note':admin_note},
        list(set([student.email_address, student.user.email]))
    )