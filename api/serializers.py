from django.contrib.auth.models import Group
from users.models import User
from sources.models import Chats,Facebook, Web, Twitter,WhatsApp, SafePal
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email','firstname','lastname']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = ['chat_sender','chat_receiver', 'chat_message','chat_session','chat_source'] #("__all__") #

class WebSerializer(serializers.ModelSerializer):
    class Meta:
        model = Web
        fields = ("__all__") #["reporter_name", "reporter_phone", "reporter_email", "reporter_location", "reporter_landmark","client_name", "client_gender", "client_ageyears", "client_location", "client_landmark","case_narrative","case_reported","source","perpetrator_is"] #("__all__")

class FacebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facebook
        fields = ("__all__")

class WhatsAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsApp
        fields = ['wa_unique','wa_message','wa_from','wa_dump'] # ("__all__")

class TwitterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Twitter
        fields = ("__all__")

class SafePalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafePal
        fields = ("__all__")
