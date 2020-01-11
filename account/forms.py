from django import forms

from . import models

#sign in form
class SigninForm(forms.Form):
    """Sign in form for the application"""

    username = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Email / username'}))
    password = forms.CharField(max_length=20, required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username:
            raise forms.ValidationError({'username': ['Enter Email / username!']})
        else:
            if len(password) < 8:
                raise forms.ValidationError({'password': ['Password is too short!']})
            else:
                user = models.EmailOrUsernameModelBackend.authenticate(self, username=username, password=password)

                if not user:
                    raise forms.ValidationError("Username / Email or Password not matched!")
                else:
                    if not user.is_active:
                        raise forms.ValidationError('Account blocked! Please contact customer support!')


    def signin(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        user = models.EmailOrUsernameModelBackend.authenticate(self, username=username, password=password)
        return user
