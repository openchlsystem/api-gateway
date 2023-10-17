from django.apps import AppConfig
from threading import Thread
import os,base64,requests,time
from datetime import datetime
import locale,random,string
from django.utils import timezone
from holla import settings,hollachoices as HC

class SourcesThread(Thread):
    def run(self):
        from sources.models import SafePal

        while True:
            cases = list(SafePal.objects.filter(chl_case_id="").values())
            for case in cases:
                case = {
                        "chat_sender": case.get('survivor_contact_phone_number'),
                        "chat_receiver": "",
                        "chat_message": base64.b64encode(str(case).encode()),
                        "chat_session": HC.getRandomString(),
                        "chat_dump": case,
                        "chat_response": "",
                        "chat_source": 'INBOX',
                        "chat_channel": 'safepal',
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

                print("THE CASE: %s " % json_response)
                case = SafePal.objects.get(pk=chat_data.get('id'))
                print("THE CASE: %s " % json_response)
                case.chl_case_id = response['messages'][0][0]
                case.save()
            except Exception as err:
                print(f'Other helpline chat error occurred: {err}') 
                return f'Other helpline chat error occurred: {err}'

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
