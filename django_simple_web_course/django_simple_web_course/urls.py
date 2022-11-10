"""django_simple_web_course URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django_registration.backends.activation.views import RegistrationView
from users.forms import CustomUserRegistrationForm
from users.forms import UserPasswordResetForm, UserLoginForm
from django.contrib.auth.views import PasswordResetView, LoginView

urlpatterns = [
    #to get custom styling override other apps by going first in accounts
    path('accounts/password_reset/', PasswordResetView.as_view(
    template_name='registration/password_reset_form.html',
    form_class=UserPasswordResetForm),name='password_reset'),
    path('accounts/login/', LoginView.as_view(template_name="registration/login.html",
        authentication_form=UserLoginForm), name='login'),
    re_path(r'^accounts/register/$',RegistrationView.as_view(form_class=CustomUserRegistrationForm),
        name='django_registration_register',),


    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('grappelli/', include('grappelli.urls')), # grappelli URLS
]

#if we're debugging serve the media files, don't do this in prod
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

