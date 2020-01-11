from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from . import forms
from . import serializers


#signout
def signout_request(request):
    """signout view for the application"""

    logout(request)
    return redirect('home:index')


class SignIn(View):
    """Sign in view for the application"""

    template_name = 'account/sign-in.html'

    def get(self, request):
        #sign in form
        form = forms.SigninForm()

        variables = {
            'form': form
        }

        return render(request, self.template_name, variables)

    def post(self, request):
        form = forms.SigninForm(request.POST or None)

        if form.is_valid():
            #form has custom function called signin() that returns valid user from db
            user = form.signin()

            #login with email or username that come from account.models
            login(request, user, backend='account.models.EmailOrUsernameModelBackend')
            return redirect('home:index')

        variables = {
            'form': form
        }

        return render(request, self.template_name, variables)



class ApiSignIn(ObtainAuthToken):
    """Sign in api view"""
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
