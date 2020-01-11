from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('sign-in/', views.SignIn.as_view(), name='sign_in'),
    path('api/sign-in/', views.ApiSignIn.as_view(), name='api_sign_in'),

    path('sign-out/', views.signout_request, name='sign_out')
]
