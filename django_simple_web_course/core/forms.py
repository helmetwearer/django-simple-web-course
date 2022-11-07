from django.forms import Form, ModelForm, HiddenInput
from django import forms
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
    CoursePageMedia, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion)

from django.utils.safestring import mark_safe


class StudentVerificationForm(Form):
    VERIFIED_CHOICES = [('R','Rejected'),('A','Approved')]
    verified = forms.CharField(label='Verification', widget=forms.RadioSelect(choices=VERIFIED_CHOICES))

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
