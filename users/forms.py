from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import Profile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    user_type = forms.ChoiceField(choices=Profile.USER_TYPES, label='I am a')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # Optional: adds spacing and Bootstrap classes automatically
        self.helper.layout = Layout(
            Field('username', css_class='form-control mb-3'),
            Field('email', css_class='form-control mb-3'),
            Field('password1', css_class='form-control mb-3'),
            Field('password2', css_class='form-control mb-3'),
            Field('user_type', css_class='form-control mb-3'),
            Submit('submit', 'Register', css_class='btn btn-primary w-100')
        )
