from django.forms import Form, ModelForm, HiddenInput
from django import forms
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
    CoursePageMedia, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion)
from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, UsernameField
from django.utils.safestring import mark_safe

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            'class': 'form-control form-control-user', 'type': 'email',
            'placeholder': 'Enter Email Address...'
        }
    ))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Password',
        }
    ))


class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-user',
        'placeholder': 'Enter Email Address...',
        'type': 'email',
        'name': 'email'
        }))

class StudentVerificationForm(Form):
    VERIFIED_CHOICES = [('R','Rejected'),('A','Approved')]
    verified = forms.CharField(label='Verification', widget=forms.RadioSelect(choices=VERIFIED_CHOICES))
    student_note = forms.CharField(label='(Optional) Note to student',
        widget=forms.Textarea(), required=False)

class StudentProfileForm(ModelForm):

    class Meta:
        model = Student
        fields = ['prefix', 'first_name', 'middle_name', 'last_name', 'suffix',
        'email_address', 'primary_phone_number', 'mobile_phone_number',
        'home_phone_number', 'fax_number', 'work_number']

class StudentIdentificationDocumentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        retval = super(StudentIdentificationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['document_title'].widget = HiddenInput()
        self.fields['document_description'].widget = HiddenInput()
        if self.instance and self.instance.verified:
            self.fields['document'].disabled = True


    def __str__(self, *args, **kwargs):

        return mark_safe('''
            <h3>%s</h3>
            <p>%s</p>
            %s
        ''' % ( self.instance.document_title, self.instance.document_description, self.render())
        )

    class Meta:
        model = StudentIdentificationDocument
        fields = ['document_title', 'document_description','document']
        help_texts = {
            'document_title': None,
            'document_description': None,
            'document': None,
        }
