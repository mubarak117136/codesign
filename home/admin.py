from django.contrib import admin

from . import models

admin.site.register(models.ColorPallete)
admin.site.register(models.Color)
admin.site.register(models.Favourite)
