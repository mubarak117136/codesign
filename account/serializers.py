from rest_framework import serializers

from . import models

#sign in
class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username", allow_blank=True)
    password = serializers.CharField(
        label="Password",
        allow_blank=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username:
            raise serializers.ValidationError({'username': ['Enter username!']})
        else:
            if not password:
                raise serializers.ValidationError({'password': ['Enter password!']})


        if username and password:
            user = models.EmailOrUsernameModelBackend.authenticate(self, username=username, password=password)

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            else:
                if not user.is_active:
                    raise serializers.ValidationError('User account disabled! Contact customer support!')
        else:
            msg = 'Must include "username / email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
