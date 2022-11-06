from django_registration.forms import RegistrationForm

from .models import User


class CustomUserRegistrationForm(RegistrationForm):

    class Meta:
        model = User
        fields = [
            User.USERNAME_FIELD,
            User.get_email_field_name(),
            "password1",
            "password2",
        ]


