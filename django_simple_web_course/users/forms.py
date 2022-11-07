from django_registration.forms import RegistrationForm

from .models import User

class CustomUserRegistrationForm(RegistrationForm):

    def __init__(self, *args, **kwargs):
        retval = super(CustomUserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['first_name'].widget.attrs.update({'autofocus': 'autofocus',
            'required': 'required', 'tabindex':'1'})
        self.fields['first_name'].widget.attrs
        self.fields['last_name'].required = True
        self.fields['last_name'].widget.attrs['tabindex'] = 2
        self.fields[User.USERNAME_FIELD].widget.attrs['tabindex'] = 3
        self.fields[User.USERNAME_FIELD].widget.attrs.pop("autofocus", None)
        self.fields[User.get_email_field_name()].widget.attrs['tabindex'] = 3
        self.fields[User.get_email_field_name()].widget.attrs.pop("autofocus", None)
        self.fields['password1'].widget.attrs['tabindex'] = 4
        self.fields['password2'].widget.attrs['tabindex'] = 5

        return retval

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            User.USERNAME_FIELD,
            User.get_email_field_name(),
            'password1',
            'password2',
        ]


