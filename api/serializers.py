from django.contrib.auth.models import Group
from users.models import User
from sources.models import Chats,Facebook, Web, Twitter,WhatsApp, SafePal,SMS,Conversations,Contacts
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

class SmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        fields = ("__all__")

class ConversationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversations
        fields = ("__all__")

class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
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
        fields = ["incident_report_id","survivor_name","survivor_gender","survivor_contact_phone_number","survivor_contact_email","survivor_age","unique_case_number","incident_location","incident_date_and_time","incident_type","incident_description","incident_reported_by","number_of_perpetrators","perpetrator_name","perpetrator_gender","perpetrator_estimated_age","perpetrator_relationship","perpetrator_location","date_of_interview_with_cso"]
