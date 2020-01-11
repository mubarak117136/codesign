from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('api/color-palletes/all/', views.AllColorPalletesApi.as_view(), name='all_color_palletes_api'),

    #color pallete detail page
    path('<int:id>/', views.ColorDetail.as_view(), name='color_detail'),
    path('api/<int:id>/', views.ColorDetailApi.as_view(), name='color_detail_api'),

    #create color pallete page
    path('create/color/', views.CreateColor.as_view(), name='create_color'),

    #my palletes
    path('dashboard/', views.MyPallete.as_view(), name='my_pallete'),
    path('favourite/', views.Favourite.as_view(), name='favourite'),
    path('favourite/remove/<int:id>/', views.RemoveFavourite.as_view(), name='remove_favourite'),

    #create color pallete api
    path('api/color-pallete/create/', views.ColorPalleteCreateApi.as_view(), name='color_pallete_create_api'),
]
