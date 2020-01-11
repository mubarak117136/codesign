from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

#import serializer
from . import serializers
from . import paginations

from . import models


class Index(View):
    """Application home page"""

    template_name = 'home/index.html'

    def get(self, request):
        #check user authenticated or not
        if request.user.is_authenticated:
            palletes = models.ColorPallete.objects.all().order_by('-date')
        else:
            palletes = models.ColorPallete.objects.filter(is_private=False).order_by('-date')

        #check if query string exists or not....its for searching
        q = request.GET.get('q')
        if q:
            palletes = palletes.filter(name__icontains=q)

        #count total palletes
        pallete_count = palletes.count()

        #pagnation
        page = request.GET.get('page', 1)
        paginator = Paginator(palletes, 3)

        try:
            palletes = paginator.page(page)
        except PageNotAnInteger:
            palletes = paginator.page(1)
        except EmptyPage:
            palletes = paginator.page(paginator.num_pages)


        index = palletes.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index

        page_range = list(paginator.page_range)[start_index:end_index]

        currently_displayed_lower = palletes.start_index()
        currently_displayed_upper = palletes.end_index()
        #end pagination

        variables = {
            'palletes': palletes,
            'pallete_count': pallete_count,
            'page_range': page_range,
            'currently_displayed_lower': currently_displayed_lower,
            'currently_displayed_upper': currently_displayed_upper,
        }
        return render(request, self.template_name, variables)



#all color palletes api
class AllColorPalletesApi(ListAPIView):
    serializer_class = serializers.ColorPalletesSerializers
    pagination_class = paginations.ColorPalletesPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            color_palletes = models.ColorPallete.objects.all().order_by('-date')
        else:
            color_palletes = models.ColorPallete.objects.filter(is_private=False).order_by('-date')
        return color_palletes



class CreateColor(View):
    """create color palletes view. color palletes is created using api from that page"""

    template_name = 'home/color/color-pallete-create.html'

    def get(self, request):
        return render(request, self.template_name)



class ColorDetail(View):
    """Color palletes detail page"""

    template_name = 'home/color/color-detail.html'

    def get(self, request, id):
        #get the color palletes using id
        color_pallete = get_object_or_404(models.ColorPallete, id=id)

        #get associated colors
        colors = models.Color.objects.filter(pallete=color_pallete)

        #check color pallets is private and user is not authenticated
        if not request.user.is_authenticated and color_pallete.is_private:
            raise Http404

        #check if requested user has a favourite the color palletes
        check_my_fav = None
        if request.user.is_authenticated:
            check_my_fav = models.Favourite.objects.filter(Q(user=request.user) & Q(pallete=color_pallete)).exists()

        variables = {
            'color_pallete': color_pallete,
            'colors': colors,
            'check_my_fav': check_my_fav
        }
        return render(request, self.template_name, variables)

    def post(self, request, id):
        color_pallete = get_object_or_404(models.ColorPallete, id=id)
        colors = models.Color.objects.filter(pallete=color_pallete)

        #added to favourate list to a user
        if request.POST.get('add_to_fav') == 'add_to_fav':
            add_to_fav = models.Favourite(user=request.user, pallete=color_pallete)
            add_to_fav.save()
            return redirect('home:color_detail', id=id)

        #delete color palletes if he own it
        if request.POST.get('delete') == 'delete':
            if request.user == color_pallete.user:
                color_pallete.delete()
                return redirect('home:index')

        #change color palletes status if he own it
        if request.POST.get('public') == 'public':
            if request.user == color_pallete.user:
                color_pallete.is_private = False
                color_pallete.save()
                return redirect('home:color_detail', id=id)

        #change color palletes status if he own it
        if request.POST.get('private') == 'private':
            if request.user == color_pallete.user:
                color_pallete.is_private = True
                color_pallete.save()
                return redirect('home:color_detail', id=id)

        variables = {
            'color_pallete': color_pallete,
            'colors': colors
        }

        return render(request, self.template_name, variables)




class ColorDetailApi(APIView):
    """color pallete details api"""

    def get(self, request, id):
        #get the color palletes using id
        color_pallete = get_object_or_404(models.ColorPallete, id=id)

        if not request.user.is_authenticated and color_pallete.is_private:
            raise Http404

        #check if requested user has a favourite the color palletes
        check_my_fav = None
        if request.user.is_authenticated:
            check_my_fav = models.Favourite.objects.filter(Q(user=request.user) & Q(pallete=color_pallete)).exists()

        #pallete json
        pallete_dict = {
            "user": color_pallete.user.username,
            "name": color_pallete.name,
            "is_private": color_pallete.is_private
        }

        #get associated colors
        colors = models.Color.objects.filter(pallete=color_pallete)
        colors_json = []
        for color in colors:
            type = color.type
            color_code = color.color_code
            c_dict = {
                "type": type,
                "color_code": color_code
            }
            colors_json.append(c_dict)

        return Response({
            'pallete': pallete_dict,
            'colors': colors_json,
            'favourite': check_my_fav
        }, status=status.HTTP_200_OK)

#=======================================================================================================================
#=======================================================================================================================
#                                                   MY PALLETE
#=======================================================================================================================
#=======================================================================================================================

#permission mixin class for user dashboard
class DashboardPermissionMixin(object):
    def has_permissions(self, request):
        return request.user.is_authenticated

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions(request):
            return redirect('home:index')
        return super(DashboardPermissionMixin, self).dispatch(
            request, *args, **kwargs)


#all color palletes create by user
class MyPallete(DashboardPermissionMixin, View):
    template_name = 'home/dashboard/my-pallete.html'

    def get(self, request):
        palletes = models.ColorPallete.objects.filter(user=request.user).order_by('-date')

        pallete_count = palletes.count()

        #pagnation
        page = request.GET.get('page', 1)
        paginator = Paginator(palletes, 3)

        try:
            palletes = paginator.page(page)
        except PageNotAnInteger:
            palletes = paginator.page(1)
        except EmptyPage:
            palletes = paginator.page(paginator.num_pages)


        index = palletes.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index

        page_range = list(paginator.page_range)[start_index:end_index]

        currently_displayed_lower = palletes.start_index()
        currently_displayed_upper = palletes.end_index()
        #end pagination

        variables = {
            'palletes': palletes,
            'pallete_count': pallete_count,
            'page_range': page_range,
            'currently_displayed_lower': currently_displayed_lower,
            'currently_displayed_upper': currently_displayed_upper,
        }
        return render(request, self.template_name, variables)


#all favourite add by user
class Favourite(DashboardPermissionMixin, View):
    template_name = 'home/dashboard/favourite.html'

    def get(self, request):
        favs = models.Favourite.objects.filter(user=request.user).order_by('-date')

        favs_count = favs.count()

        #pagnation
        page = request.GET.get('page', 1)
        paginator = Paginator(favs, 3)

        try:
            favs = paginator.page(page)
        except PageNotAnInteger:
            favs = paginator.page(1)
        except EmptyPage:
            favs = paginator.page(paginator.num_pages)


        index = favs.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index

        page_range = list(paginator.page_range)[start_index:end_index]

        currently_displayed_lower = favs.start_index()
        currently_displayed_upper = favs.end_index()
        #end pagination

        variables = {
            'favs': favs,
            'favs_count': favs_count,
            'page_range': page_range,
            'currently_displayed_lower': currently_displayed_lower,
            'currently_displayed_upper': currently_displayed_upper,
        }
        return render(request, self.template_name, variables)


#remove from favourite if he own
class RemoveFavourite(DashboardPermissionMixin, View):
    def get(self, request, id):
        fav = get_object_or_404(models.Favourite, id=id, user=request.user)
        fav.delete()
        return redirect('home:favourite')

#=======================================================================================================================
#=======================================================================================================================
#                                                   END MY PALLETE
#=======================================================================================================================
#=======================================================================================================================



#=======================================================================================================================
#=======================================================================================================================
#                                                   CREATE COLOR PALLETE API
#=======================================================================================================================
#=======================================================================================================================


class ColorPalleteCreateApi(APIView):
    """Color palletes create api"""

    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.CreateColorPalleteSerializers

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.deploy(user=request.user)
            return Response({
                'message': 'Color pallete created successfully!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#=======================================================================================================================
#=======================================================================================================================
#                                                   CREATE COLOR PALLETE API
#=======================================================================================================================
#=======================================================================================================================
