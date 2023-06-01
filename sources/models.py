from random import choices
import uuid
from email.policy import default
from pyexpat import model
from django.utils import timezone
from django.db import models
from holla import hollachoices as HC

# Create your models here.

class SMS(models.Model):
    sms_text = models.TextField()
    sms_phone = models.IntegerField()
    sms_status = models.CharField(max_length=100)
    sms_sent_status = models.CharField(max_length=100)
    sms_schedule_date = models.DateTimeField(default=timezone.now)
    sms_cost = models.IntegerField()

class Chats(models.Model):
    chat_sender = models.CharField(max_length=100,blank=True)
    chat_receiver = models.CharField(max_length=100,blank=True)
    chat_message = models.TextField(blank=False)
    chat_session = models.TextField(blank=False)
    chat_time = models.DateTimeField(auto_now_add=True)
    chat_status = models.BooleanField(default=False)
    chat_dump = models.JSONField(default=list())
    chat_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    chat_response = models.CharField(max_length=100,blank=True)
    chat_source = models.CharField(max_length=100,choices=HC.CHAT_SOURCES,default='WENI')
    chat_channel = models.CharField(max_length=100,choices=HC.CHAT_CHANNELS,default='WENI')

# class MAIL(models.Model):
#     mail_sender = models.IntegerField(blank=False)
#     mail_receiver = models.IntegerField(blank=False)
#     mail_cc = models.IntegerField(blank=False)
#     mail_bcc = models.IntegerField(blank=False)
#     mail_message = models.TextField(blank=False)
#     mail_attachments = models.CharField(max_length=200)
#     mail_box = models.CharField(max_length=20)
#     mail_date = models.DateTimeField()
#     mail_time = models.DateTimeField(auto_created=True)
#     mail_status = models.CharField(max_length=100)
class Web(models.Model):
    reporter_name = models.CharField(max_length=100,default="")
    reporter_phone = models.CharField(max_length=100,default="")
    reporter_email = models.CharField(max_length=100,default="")
    reporter_location = models.CharField(max_length=100,default="")
    reporter_landmark = models.CharField(max_length=100,default="")
    reporter_gender= models.CharField(max_length=100,default="")

    client_name = models.CharField(max_length=100,default="")
    client_gender = models.CharField(max_length=100,default="")
    client_ageyears = models.CharField(max_length=100,default="")
    client_location = models.CharField(max_length=100,default="")
    client_landmark = models.CharField(max_length=100,default="")
    client_agemonths = models.CharField(max_length=100,default="")
    client_guardian = models.CharField(max_length=100,default="")

    perpetrator_name = models.CharField(max_length=100,default="")
    perpetrator_phone = models.CharField(max_length=100,default="")
    perpetrator_email = models.CharField(max_length=100,default="")
    perpetrator_location = models.CharField(max_length=100,default="")
    perpetrator_landmark = models.CharField(max_length=100,default="")
    perpetrator_gender = models.CharField(max_length=100,default="")

    case_narrative = models.TextField(default="")
    case_reported = models.CharField(max_length=100,default="")
    perpetrator_is = models.CharField(max_length=100,default="")
    source = models.CharField(max_length=100,default="")
    case_justice = models.CharField(max_length=100,default="")
    additional_fields = models.JSONField(default={})
    case_date = models.DateTimeField(auto_now_add=True)

class Contacts(models.Model):
    cont_name = models.CharField(max_length=100)
    cont_phone = models.CharField(max_length=20)
    cont_email = models.CharField(max_length=200)
    cont_physical_address = models.CharField(max_length=200)
    cont_postal_address = models.CharField(max_length=100)
    cont_postal_code = models.IntegerField()
    cont_city = models.CharField(max_length=100)
    #cont_country = models.ForeignKey(Countries,on_delete=models.CASCADE)
    #cont_member = models.ForeignKey(Persons,on_delete=models.CASCADE)
    cont_group = models.CharField(max_length=200)


class Emails(models.Model):
    mail_body = models.TextField()
    mail_address_from = models.CharField(max_length=100)
    mail_address_to = models.CharField(max_length=100)
    mail_address_cc = models.CharField(max_length=200)
    mail_status = models.CharField(max_length=100)
    mail_date = models.DateTimeField(auto_now_add=True)

class Facebook(models.Model):
    fb_unique = models.CharField(max_length=200)
    fb_message = models.TextField()
    fb_datetime = models.DateTimeField(auto_now_add=True)
    fb_status = models.CharField(max_length=20,default="NEW")
    fb_direction = models.CharField(max_length=20,default="INBOX")
    fb_from = models.CharField(max_length=50,default="")
    fb_to = models.CharField(max_length=50,default="")
    fb_dump = models.JSONField()
    
class Twitter(models.Model):
    tw_unique = models.CharField(max_length=200)
    tw_message = models.TextField()
    tw_datetime = models.DateTimeField(auto_now_add=True)
    tw_status = models.CharField(max_length=20,default="NEW")
    tw_direction = models.CharField(max_length=20,default="INBOX")
    tw_from = models.CharField(max_length=50,default="")
    tw_to = models.CharField(max_length=50,default="")
    tw_dump = models.JSONField(default=[])

class WhatsApp(models.Model):
    wa_unique = models.CharField(max_length=200)
    wa_message = models.TextField()
    wa_datetime = models.DateTimeField(auto_now_add=True)
    wa_status = models.CharField(max_length=20,default="NEW")
    wa_direction = models.CharField(max_length=20,default="INBOX")
    wa_from = models.CharField(max_length=50,default="")
    wa_to = models.CharField(max_length=50,default="")
    wa_dump = models.JSONField(default=[])

class Telegram(models.Model):
    tl_unique = models.CharField(max_length=200)

class SafePal(models.Model):
    incident_report_id = models.IntegerField()
    survivor_name = models.CharField(max_length=200)
    survivor_gender = models.CharField(max_length=200)
    survivor_contact_phone_number = models.CharField(max_length=200)
    survivor_contact_email = models.CharField(max_length=200)
    survivor_age = models.CharField(max_length=200)
    unique_case_number = models.CharField(max_length=200) 
    incident_location = models.CharField(max_length=200)
    incident_date_and_time = models.CharField(max_length=200)
    incident_type = models.CharField(max_length=200)
    incident_description = models.CharField(max_length=200)
    incident_reported_by = models.CharField(max_length=200)
    number_of_perpetrators = models.CharField(max_length=200)
    perpetrator_name = models.CharField(max_length=200)
    perpetrator_gender = models.CharField(max_length=200) 
    perpetrator_estimated_age = models.CharField(max_length=200)
    perpetrator_relationship = models.CharField(max_length=200)
    perpetrator_location = models.CharField(max_length=200)
    date_of_interview_with_cso = models.CharField(max_length=200)
    chl_status = models.CharField(max_length=200)
    chl_case_id = models.CharField(max_length=200)
    chl_time = models.DateTimeField(auto_created=True)
    chl_user_id = models.CharField(max_length=200)


