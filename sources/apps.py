from django.apps import AppConfig
from threading import Thread
import os,base64,requests,time
from datetime import datetime
import json
from django.utils import timezone
from holla import settings,hollachoices as HC

class SourcesThread(Thread):
    """
    Thread to provide data push for integrations on the sources
    """
    def run(self):
        from sources.models import SafePal

        while True:
            cases = list(SafePal.objects.filter(chl_case_id="").values('id', 'incident_report_id', 'survivor_name', 'survivor_gender','survivor_contact_phone_number','survivor_contact_email', 'survivor_age', 'unique_case_number','incident_location','incident_date_and_time','incident_type','incident_description','incident_reported_by','number_of_perpetrators','perpetrator_name','perpetrator_gender','perpetrator_estimated_age','perpetrator_relationship','perpetrator_location','date_of_interview_with_cso','chl_status','chl_case_id', 'chl_user_id'))
            for case in cases:
                case = {
                        "chat_sender": case.get('survivor_contact_phone_number'),
                        "chat_receiver": "",
                        "chat_message": base64.b64encode(json.dumps(case).encode()),
                        "chat_session": HC.getRandomString(),
                        "chat_dump": case,
                        "chat_response": "",
                        "chat_source": "INBOX",
                        "chat_channel": "safepal",
                        "id":case['id']
                    }
                
                sent = self.sendtohelpline(case)

    def sendtohelpline(self,chat_data):
        from sources.models import SafePal
        # send chat to helpline
        caseid=False
        token = False
        try:

            headers = {
                "authorization":"Basic %s" % settings.HELPLINE_TOKEN,
                "accept": "*/*"
                }

            response = requests.post(settings.HELPLINE_BASE,headers=headers)
            json_response = response.json()

            # if it failed to get token, return
            if json_response.get('errors',False):
                return "Helpline chat token error: %s " % json_response
            
            token = json_response["ss"][0][0]

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except Exception as err:
            print(f'Other token error occurred: {err}') 
            return f'Other token error occurred: {err}'
        else:
            print('Token Success!')

        if token:
            try:
                tm = time.mktime(datetime.now().timetuple())
                chat = {
                    "channel":chat_data.get('chat_channel'),
                    "from":chat_data.get('chat_sender'),
                    "message":chat_data.get('chat_message').decode(),
                    "timestamp":tm,
                    "session_id":chat_data.get('chat_session'),
                    "message_id":chat_data['id']
                }
                
                headers = {"Authorization":"Bearer %s" % token,'Content-Type':'application/json' }

                response = requests.post('%smsg/' % settings.HELPLINE_BASE, json=chat,headers=headers)
                
                json_response = response.json()
                print("Helpline chat response: %s " % json_response)
                # if it failed to create chat, return
                if json_response.get('errors',False):
                    return "Helpline chat error: %s " % json_response
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
                case = SafePal.objects.get(pk=chat_data.get('id'))
                case.chl_case_id = json_response["messages"][0][0]
                case.save()
            except Exception as err:
                print(f'Other helpline chat error occurred: {err}') 
                return f'Other helpline chat error occurred: {err}'

    def send_sms(self):
        from sources.models import SMS
        try:
            messages = SMS.objects.filter(sms_direction='OUTBOX',sms_status=0)

            if len(messages) > 0:
                for message in messages:
                    # send sms 
                    data =	{
                        'recipients':message.sms_phone,
                        'message'	:message.sms_text,	
                        'sender':settings.SMS_ID,
                        'dlrurl':'https://call.solektra.rw/api/sources/sms/'
                    }
                    response = requests.post('https://www.intouchsms.co.rw/api/sendsms/.json',data,auth=(settings.SMS_USN,settings.SMS_PASS))
                    json_response = response.json()
                    ms_status = {'P':4,'D':5,'Q':2,'E':3,'S':1}
                    
                    if int(response.status_code) == 200:
                        if(json_response.get('success')):
                            message.sms_status = 1
                            message.sms_sent_status = ms_status.get(str(json_response.get('details')[0].get('status')))
                            message.sms_cost = json_response.get('details')[0].get('cost')
                            message.sms_response = json_response
                            message.sms_messageid = json_response.get('details')[0].get('messageid')
                            message.save()
                        else:
                            # print(json_response.get('response')[0])
                            message.sms_status = 1
                            # if not json_response.get('response')[0].get('errors').get('error').lower() == 'balance':
                            #     message.sms_sent_status = 3
                            message.sms_response = json_response
                            message.save()
                    else:
                        # message.sms_status = 1
                        message.sms_response = json_response
                        message.save()

                # update sms status
            # 
        except Exception as e:
            print("Error Sending SMS: %s " % e.args[0])
            
    def send_whatsapp(self):
        from sources.models import WhatsApp
        try:
            messages = WhatsApp.objects.filter(wa_direction='OUTBOX',wa_status="DRAFT")
            
            if len(messages) > 0:
                for message in messages:
                    data =	{
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": message.wa_contact,
                        "type": "text",
                        "text":{
                            "preview_url": "false",
                            "body": message.wa_message
                        }
                    }

                    header = {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer %s " % settings.FB_TOKEN
                    }
                    
                    response = requests.post('https://graph.facebook.com/v18.0/%s/messages' % settings.WA_PHONE_ID,json=data,headers=header)
                    json_response = response.json()
                    
                    if int(response.status_code) == 200:
                        message.wa_status = 'SENT'
                        message.wa_unique = json_response.get('messages')[0].get("id")
                        message.save()
                    else:
                        message.wa_status = 'FAILED'
                        message.wa_response = json_response
                        message.save()

                # update sms status
            # 
        except Exception as e:
            print("Error Sending SMS: %s " % e.args[0])


class SourcesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sources'

    def ready(self):
        run_once = os.environ.get('SOURCETHREAD',False)         
        if run_once:
            return
        os.environ['SOURCETHREAD'] = 'True'

        t = SourcesThread()
        t.daemon = True
        t.start()
