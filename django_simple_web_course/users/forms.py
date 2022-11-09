from django_registration.forms import RegistrationForm

from .models import User

class CustomUserRegistrationForm(RegistrationForm):

    def __init__(self, *args, **kwargs):
        retval = super(CustomUserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['first_name'].widget.attrs.update({'autofocus': 'autofocus',
            'required': 'required', 'tabindex':'1', 'class': 'form-control form-control-user',
            'placeholder':'First Name'})
        self.fields['last_name'].required = True
        self.fields['last_name'].widget.attrs['tabindex'] = 2
        self.fields['last_name'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields[User.USERNAME_FIELD].widget.attrs['tabindex'] = 3
        self.fields[User.USERNAME_FIELD].widget.attrs.pop("autofocus", None)
        self.fields[User.USERNAME_FIELD].widget.attrs['class'] = 'form-control form-control-user'
        self.fields[User.USERNAME_FIELD].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['tabindex'] = 4
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['tabindex'] = 5
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-user'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

        return retval

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            User.USERNAME_FIELD,
            'password1',
            'password2',
        ]


