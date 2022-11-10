from django_registration.forms import RegistrationForm
from django import forms
from .models import User
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


