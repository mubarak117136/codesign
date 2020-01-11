from django.db import models
from django.contrib.auth.models import User


class ColorPallete(models.Model):
    """Color pallete model"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)

    is_private = models.BooleanField(default=False, null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    """Color that associated with color palletes"""

    pallete = models.ForeignKey(ColorPallete, on_delete=models.CASCADE, null=True, blank=True)

    type = models.CharField(max_length=10, null=True, blank=True) #dominant / accent
    color_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.pallete.name


class Favourite(models.Model):
    """User favourite color palletes"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pallete = models.ForeignKey(ColorPallete, on_delete=models.CASCADE, null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.username
