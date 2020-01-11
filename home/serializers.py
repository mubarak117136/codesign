from rest_framework import serializers
import json

from . import models

class CreateColorPalleteSerializers(serializers.Serializer):
    """Color pallete serializer"""

    name = serializers.CharField(max_length=50, required=False, allow_null=True)
    is_private = serializers.BooleanField(required=False, allow_null=True)

    #colors is a json field which contains type and color code as a json format for Color model
    colors = serializers.JSONField(allow_null=True, required=False)


    def validate(self, data):
        name = data.get('name')
        is_private = data.get('is_private')
        colors = data.get('colors')

        if not name:
            raise serializers.ValidationError({'name': ['Enter color name!']})
        else:
            if len(name) > 50:
                raise serializers.ValidationError({'name': ['Name must be less than 50 characters!']})

        if not colors:
            raise serializers.ValidationError({'colors': ['Select colors!']})
        return data


    def deploy(self, user):
        """save color palletes if everything is ok"""

        name = self.validated_data.get('name')
        is_private = self.validated_data.get('is_private')
        colors = self.validated_data.get('colors')

        #create color pallete model
        color_pallete = models.ColorPallete(user=user, name=name, is_private=is_private)
        color_pallete.save()

        #create color model for specific color pallete
        if color_pallete:
            for color in colors:
                type = color["type"]
                color_code = color["code"]
                color = models.Color(pallete=color_pallete, type=type, color_code=color_code)
                color.save()


#all color palletes serializer
class ColorPalletesSerializers(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = models.ColorPallete
        fields = ('user', 'name', 'is_private', 'date')
