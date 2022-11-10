from django.forms import Form, ModelForm, HiddenInput
from django import forms
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
    CoursePageMedia, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion)
from django.utils.safestring import mark_safe
from intl_tel_input.widgets import IntlTelInputWidget


class StudentVerificationForm(Form):
    VERIFIED_CHOICES = [('R','Rejected'),('A','Approved')]
    verified = forms.CharField(label='Verification', widget=forms.RadioSelect(choices=VERIFIED_CHOICES))
    student_note = forms.CharField(label='(Optional) Note to student',
        widget=forms.Textarea(), required=False)

class StudentProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        retval = super(StudentProfileForm, self).__init__(*args, **kwargs)
        self.fields['prefix'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['first_name'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['middle_name'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['last_name'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['suffix'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['primary_phone_number'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['primary_phone_number'].error_messages['invalid'] = 'Please enter in a valid phone number'
        self.fields['mobile_phone_number'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['mobile_phone_number'].error_messages['invalid'] = 'Please enter in a valid phone number'
        self.fields['home_phone_number'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['home_phone_number'].error_messages['invalid'] = 'Please enter in a valid phone number'
        self.fields['fax_number'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['fax_number'].error_messages['invalid'] = 'Please enter in a valid phone number'
        self.fields['work_number'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['work_number'].error_messages['invalid'] = 'Please enter in a valid phone number'
        self.fields['email_address'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['email_address'].disabled = True

        return retval

    class Meta:
        model = Student
        fields = ['prefix', 'first_name', 'middle_name', 'last_name', 'suffix',
        'email_address', 'primary_phone_number', 'mobile_phone_number',
        'home_phone_number', 'fax_number', 'work_number']
        widgets = {
            'primary_phone_number': IntlTelInputWidget(),
            'mobile_phone_number': IntlTelInputWidget(),
            'home_phone_number': IntlTelInputWidget(),
            'fax_number': IntlTelInputWidget(),
            'work_number': IntlTelInputWidget(),
        }



class StudentIdentificationDocumentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        retval = super(StudentIdentificationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['document_title'].widget = HiddenInput()
        self.fields['document_description'].widget = HiddenInput()
        if self.instance and self.instance.verified:
            self.fields['document'].disabled = True

        return retval


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
