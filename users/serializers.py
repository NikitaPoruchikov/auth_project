from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'invite_code',
                  'activated_invite_code', 'referred_by']


class UserInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['invite_code']
