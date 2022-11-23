from django import forms
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
    CoursePageMedia, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion, 
    CourseTestQuestionAnswerOption)
from django.utils.safestring import mark_safe
from intl_tel_input.widgets import IntlTelInputWidget
from django.core.exceptions import ValidationError
from uuid import UUID


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test

class RetakeApprovalForm(forms.Form):
    APPROVAL_CHOICES = [('R','Rejected'),('A','Approved')]
    approved = forms.CharField(label='Retake Approval', 
        widget=forms.RadioSelect(choices=APPROVAL_CHOICES))
    student_note = forms.CharField(label='(Optional) Note to student',
        widget=forms.Textarea(), required=False)

class StudentVerificationForm(forms.Form):
    VERIFIED_CHOICES = [('R','Rejected'),('A','Approved')]
    verified = forms.CharField(label='Verification', widget=forms.RadioSelect(choices=VERIFIED_CHOICES))
    student_note = forms.CharField(label='(Optional) Note to student',
        widget=forms.Textarea(), required=False)

class TestQuestionInstanceForm(forms.Form):
    answer = forms.CharField()

    def __init__(self, *args, **kwargs):
        question_instance = kwargs.pop('question_instance')
        retval = super(TestQuestionInstanceForm, self).__init__(*args, **kwargs)
        CHOICES = [(answer.guid,answer.value) for answer in question_instance.answer_options ]
        self.fields['answer']=forms.CharField(label='', widget=forms.RadioSelect(choices=CHOICES))

    def clean_answer(self):
        guid = self.cleaned_data['answer']
        if not is_valid_uuid(guid):
            raise ValidationError("Invalid multiple choice answer")
        # valid uuid safe to look up
        try:
            answer_option = CourseTestQuestionAnswerOption.objects.get(guid=guid)
        except CourseTestQuestionAnswerOption.DoesNotExist:
            raise ValidationError("Invalid multiple choice answer")
        return answer_option.answer_option
        

class StudentProfileForm(forms.ModelForm):

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



class StudentIdentificationDocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        retval = super(StudentIdentificationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['document_title'].widget = forms.HiddenInput()
        self.fields['document_description'].widget = forms.HiddenInput()
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
