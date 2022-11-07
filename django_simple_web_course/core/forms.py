from django.forms import ModelForm
from .models import (Student, StudentIdentificationDocument, Course, CoursePage,
    CoursePageMedia, CourseTest, MultipleChoiceAnswer, MultipleChoiceTestQuestion)



class StudentProfileForm(ModelForm):

    class Meta:
        model = Student
        fields = ['prefix', 'first_name', 'middle_name', 'last_name', 'suffix',
        'email_address', 'primary_phone_number', 'mobile_phone_number',
        'home_phone_number', 'fax_number', 'work_number']

class StudentIdentificationDocumentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        retval = super(StudentIdentificationDocumentForm, self).__init__(*args, **kwargs)
        self.fields['document_title'].disabled = True
        self.fields['document_description'].disabled = True
        if self.instance and self.instance.verified:
            self.fields['document'].disabled = True

    class Meta:
        model = StudentIdentificationDocument
        fields = ['document_title', 'document_description','document']
        help_texts = {
            'document_title': None,
            'document_description': None,
            'document': None,
        }
