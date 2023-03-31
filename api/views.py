from multiprocessing import context
from random import Random
from urllib import request
from django.contrib.auth.models import Group
from django.http import JsonResponse
from rest_framework import viewsets,status
from users.models import User
from sources.models import Chats,Facebook, Web, Twitter
from rest_framework import permissions
from rest_framework.response import Response
from api.serializers import UserSerializer, GroupSerializer, ChatSerializer, FacebookSerializer, TwitterSerializer, WebSerializer
import uuid
import requests,time,ssl
from datetime import datetime
from requests.exceptions import HTTPError
from holla import settings,hollachoices as HC
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all() #.order_by('-date_joined')
    serializer_class = UserSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

class SourcesViewSet(viewsets.ViewSet):
    queryset = Web.objects.all().order_by('-id')
    serializer_class = WebSerializer

    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, format=None):
        """
        Return a list of all sources.
        """
        queryset = Web.objects.all().order_by('-id')
        serializer_class = WebSerializer(queryset, many=True)

        return Response(serializer_class.data)

    def create(self, request):
        
        posted = request.data

        serializer = self.serializer_class(data=posted)

        if serializer.is_valid():
            case = Web.objects.create(**serializer.validated_data)
            
            if case.chat_source == 'WENI':
                # push chat to helpline
                print("FROM WENI")

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request Data %s ' % request.data,
                         'message': serializer.is_valid()},
                          status=status.HTTP_400_BAD_REQUEST)

class WebViewSet(viewsets.ViewSet):
    queryset = Web.objects.all().order_by('-id')
    serializer_class = WebSerializer
    
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, format=None):
        """
        Return a list of all sources.
        """
        queryset = Web.objects.all().order_by('-id')
        serializer_class = WebSerializer(queryset, many=True)

        return Response(serializer_class.data)

    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                case = Web.objects.create(**serializer.validated_data)
                cc = self.helpline_case(case)
                return Response("Success: %s " % cc, status=status.HTTP_201_CREATED)

            #raise Exception("DEBUG")
            return Response({'status': 'Bad Request Data for %s ' % request.data,
                            'message': serializer.is_valid()},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'Bad Request %s ' % request.data,
                            'message': 'Error: %s ' % e.args[0]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def helpline_case(self,case):
        # sending case to helpline
        # get token
        token = False
        try:

            headers = {
                "authorization":"Basic %s" % settings.HELPLINE_TOKEN,
                "accept": "*/*"
                }

            response = requests.post(settings.HELPLINE_BASE,headers=headers,verify=False)
            json_response = response.json()
            token = json_response["ss"][0][0]

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP token error: {http_err}')
            return f'HTTP token error: {http_err}'
        except Exception as err:
            print(f'Other token error occurred: {err}') 
            return f'Other token error occurred: {err}'
        else:
            print('Token Success!')
        
        if token:
            try:
                headers = {
                    "Content-Type":"application/json",
                    "Authorization":"Bearer %s" % token
                    }
                
                reporter = {"fname":case.reporter_name,"landmark":case.reporter_landmark,"phone":str(case.reporter_phone).strip('+'),"email":case.reporter_email,"src":"call","src_ts":case.case_date.timestamp(),"src_uid":HC.getRandomString(),"src_callid":"","src_address":"","src_usr":"","src_vector":"1"}
                reporter_res = requests.post("%sreporters/" % settings.HELPLINE_BASE,json=reporter,headers=headers,verify=False)
                reporter = reporter_res.json()
                
                # if it failed to create reporter, return
                if reporter.get('errors',False):
                    return "Error creating helpline case: %s " %reporter
                
                reporter_id = reporter.get('reporters')[0][0]
                
                client = {"fname":case.client_name,"age":int(case.client_ageyears) + int(case.client_agemonths)/12,"age_group_id":"","landmark":case.client_landmark,"phone":"","email":"","src":"API","src_ts":"","src_uid":HC.getRandomString(5),"src_callid":"","src_address":"","src_usr":"","src_vector":"1"}
                client_res = requests.post("%sclients/" % settings.HELPLINE_BASE,json=client,headers=headers,verify=False)
                client = client_res.json()

                # if it failed to create client, return
                if client.get('errors',False):
                    return "Error creating helpline case: %s " % client
                
                client_id = client.get('clients')[0][0]

                perp_id = ""

                case = {
					"src":case.source if case.source else "API",
					"src_ts":time.mktime(case.case_date.timetuple()),
					"src_uid":HC.getRandomString(5),
					"src_callid":"",
					"src_address":case.reporter_email,
					"src_usr":"200",
					"src_vector":"2",
					"reporter_id":reporter_id,
					"reporter_contact_id":reporter_id,
					"clients":[{
						"client_id":client_id
                    }],
					"perpetrators":[{
						"perpetrator_id":perp_id
                    }],
					"attachments":[],
					"services":[{
						"category_id":"116","category_id":"362039"
                    }],
					"knowabout116_id":"362015",
					"case_category_root_id":"87",
					"gbv_related":"2",
					"case_category_id":"362534",
					"narrative":case.case_narrative,
					"plan":" ",
					"priority":"1",
					"status":"1",
					"disposition_id":"362527"}

                response = requests.post("%scases/" % settings.HELPLINE_BASE,json=case,headers=headers,verify=False)
                json_response = response.json()

                if json_response.get('errors',False):
                    return "Could not create helpline case: %s " % json_response

                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                # print(f'HTTP case error: {http_err}')
                return f'Helpline case error: {http_err}'
            except Exception as err:
                # print(f'Other case error occurred: {err}') 
                return f'Other helpline case error occurred: {err}'
            else:
                # print('Case Success!')
                return "Case Success"

class ChatViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = Chats.objects.all().order_by('-id')
    serializer_class = ChatSerializer

    def list(self, request, format=None):
        """
        Return a list of all sources.
        """
        queryset = Chats.objects.all().order_by('-id')
        serializer_class = ChatSerializer(queryset, many=True)

        return Response(serializer_class.data)


    def create(self, request,sessionid=False):
        posted = request.data
        if sessionid:
            # send close session to WENI
            # POST /api/v2/flow_starts.json
            #     "flow": "f5901b62-ba76-4003-9c62-72fdacc1b7b7",
            #     "groups": ["f5901b62-ba76-4003-9c62-72fdacc15515"],
            #     "contacts": ["f5901b62-ba76-4003-9c62-fjjajdsi15553"],
            #     "urns": ["twitter:sirmixalot", "tel:+12065551212"],
            #     "params": {"first_name": "Ryan", "last_name": "Lewis"}
            # }
            
            try:
                chat = Chats.objects.filter(chat_session=sessionid)
                chat = {
                    "flow": sessionid,
                    "groups": ["f5901b62-ba76-4003-9c62-72fdacc15515"],
                    "contacts": [chat.chat_sender],
                    "urns": ["tel:" + chat.chat_sender] #,
                    # "params": {"first_name": "Ryan", "last_name": "Lewis"}
                }

                headers = {"Authorization":"Token a8f15467cc4fd8febfac3f7694349ec07a789e64"}

                response = requests.post('https://rapidpro.ilhasoft.mobi/api/v2/flow_starts', json=chat,headers=headers)
                json_response = response.json()
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}') 
            else:
                print('Success!')

            return Response({'status':"success"}, status=status.HTTP_200_CREATED)

        posted = {
            "chat_sender": posted.get('chat_sender'),
            "chat_receiver": posted.get('chat_receiver'),
            "chat_message": posted.get('chat_message'),
            "chat_session": posted.get('chat_session'),
            "chat_dump": posted,
            "chat_response": "",
            "chat_source": posted.get('chat_source')
        }
        serializer = self.serializer_class(data=posted)

        if serializer.is_valid():
            chat = Chats.objects.create(**serializer.validated_data)
            
            if chat.chat_source == 'WENI':
                # push chat to helpline
                self.send_to_helpline(chat)
            else:
                print("SEND TO WENI")
                self.send_to_weni(chat)
                #self.send_to_facebook(chat)


            return Response({'status':"success",'uuid':chat.chat_uuid}, status=status.HTTP_201_CREATED)

        return Response({'status': 'Bad Request %s ' % request.data,
                         'message': serializer.is_valid()},
                          status=status.HTTP_400_BAD_REQUEST)
    
    def send_to_helpline(self,chat_data):
        # send chat to helpline
        token = False
        try:

            headers = {
                "authorization":"Basic %s" % settings.HELPLINE_TOKEN,
                "accept": "*/*"
                }

            response = requests.post(settings.HELPLINE_BASE,headers=headers,verify=False)
            json_response = response.json()

            # if it failed to get token, return
            if json_response.get('errors',False):
                return "Helpline chat token error: %s " % json_response
            
            token = json_response["ss"][0][0]

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            # print(f'HTTP token error: {http_err}')
            return f'HTTP token error: {http_err}'
        except Exception as err:
            # print(f'Other token error occurred: {err}') 
            return f'Other token error occurred: {err}'
        else:
            print('Token Success!')

        if token:
            try:
                tm = time.mktime(datetime.now().timetuple())
                chat = {
                    "channel":"chat",
                    "from":chat_data.chat_sender,
                    "message":chat_data.chat_message,
                    "timestamp":tm,
                    "session_id":chat_data.chat_session,
                    "message_id":chat_data.id
                }

                headers = {"Authorization":"Bearer %s" % token,'Content-Type':'application/json' }

                response = requests.post('%smsg/' % settings.HELPLINE_BASE, json=chat,headers=headers,verify=False)
                json_response = response.json()
                
                
                # if it failed to create chat, return
                if json_response.get('errors',False):
                    return "Helpline chat error: %s " % json_response
                
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                # print(f'HTTP helpline chat error occurred: {http_err}')
                return f'HTTP helpline chat error occurred: {http_err}'
            except Exception as err:
                # print(f'Other helpline chat error occurred: {err}') 
                return f'Other helpline chat error occurred: {err}'
            else:
                # print('Success!')
                return 'Chat Success'
    
    def send_to_weni(self,chat_data):
        # send chat to WENI
        try:
            chat = {
                "urns": ["tel:+254727647431"],
                "contacts": [chat_data.chat_sender],
                "text": chat_data.chat_message
            }

            headers = {"Authorization":"Token a8f15467cc4fd8febfac3f7694349ec07a789e64"}

            response = requests.post('https://rapidpro.ilhasoft.mobi/api/v2/broadcasts', json=chat,headers=headers)
            json_response = response.json()
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print('Success!')
    
    def send_to_facebook(request,chat_data):
        # 
        # send chat to WENI
        try:
            chat = {
                "recipient": {
                "id":chat_data.chat_sender, # "3412749322156758"
                },
                "message": {"text":chat_data.chat_message}
            }

            headers = {"access_token":"EAAq50PnynzgBAP6DPk5giqGSJo6TYNPcDlehl2WWGlf2vl0UvUcQiMNntECZBBekL381aGu1POPGUKJWU3hjg30PGFsYO8GFFsZAIewfCFIMD8Rwj61unfzhjIK5FUEeagZAWuGKh9D4oXeaQglZCP9K0fgK6xtLjzNyeXhHrcR8kNJY9hIeZC5mHH4ZBJJamfFrbjrsyrSAZDZD"}
            
            fburl = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAq50PnynzgBAP6DPk5giqGSJo6TYNPcDlehl2WWGlf2vl0UvUcQiMNntECZBBekL381aGu1POPGUKJWU3hjg30PGFsYO8GFFsZAIewfCFIMD8Rwj61unfzhjIK5FUEeagZAWuGKh9D4oXeaQglZCP9K0fgK6xtLjzNyeXhHrcR8kNJY9hIeZC5mHH4ZBJJamfFrbjrsyrSAZDZD&recipient=3412749322156758'

            response = requests.post(fburl, json=chat,headers=headers)
            json_response = response.json()
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print('Success!')



class FacebookViewSet(viewsets.ViewSet):

    queryset = Facebook.objects.all().order_by('-id')
    serializer_class = FacebookSerializer
    
    def list(self, request, format=None):
        """
        Return a list of all sources.
        """
        mode = request.GET.get('hub.mode',False)
        token = request.GET.get('hub.verify_token',False)
        challenge = request.GET.get('hub.challenge',False)

        if(mode and token):
            if mode == "subscribe" and token == 'aYyHMLNwmE)Y?-G};x)a2zt6wrl48gayahugfnlBx!Rfh%e&x':
                return Response(int(challenge),status=200)
            else:
                return Response(status=403)
        else:
            queryset = Facebook.objects.all().order_by('-id')
            serializer_class = FacebookSerializer(queryset, many=True)

            return Response(serializer_class.data)

    def create(self, request):
        if request.data.get('object') == 'page':
            posted = request.data.get('entry')[0].get('messaging')[0]
            response_message = "NO ACTION"

            if(posted.get('message',False)):
                message = posted.get('message')

                if not message.get('is_echo',False): # and message.get('text'):
                    recipient = posted.get('sender').get('id')
                    if (message.get('quick_reply',False)):
                        qreply = message.get('quick_reply')
                        response_message = self.handlePayload(qreply.get('payload'))
                        self.send_message(recipient,response_message)
                    elif (message.get('attachments',False)):
                        response_message = self.handleAttachmentMessage()
                    elif (message.get('text',False)):
                        response_message = self.saveItem(request.data,posted)
                        # chat_data = {

                        # }
                        # if(request.META.get('HTTP_REFERER') == 'facebook.com'):
                        #     send_to_helpline(message)
                        # else:

                        # message = {"text":"Ninafurahi kukukaribisha, naitwa  #Malezi. Mimi ni roboti  ya @SemaTanzania. Kwanza kabisa naomba tufahamiane. Kama hutojali nitakuuliza maswali mawiliili kuweza kukufahamu nakusaidia kuboresha huduma zetu."}
                        
                        # self.send_message(recipient, message)
                        # response_message = self.handlePayload()
                        # self.send_message(recipient, response_message)
                        # self.send_to_helpline()
            
            elif (posted.get('postback',False)):
                response_message = self.handlePostback()
            elif (posted.get('referral',False)):
                response_message = self.handleReferral()
            elif (posted.get('optin',False)):
                response_message = self.handleOptIn()
            elif (posted.get('pass_thread_control',False)):
                response_message = self.handlePassThreadControlHandover()

            return  Response(response_message, status=status.HTTP_200_OK)
                
        return Response({'status': 'Bad Request %s ' % request.data,
                         'message': "Could not process request"},
                          status=status.HTTP_400_BAD_REQUEST)
    def handleTextMessage(self,data,message):
        ret = self.saveItem(data,message)
    def saveItem(self,data,posted):
        
            post = {
                "fb_unique":posted.get('message').get('mid'),
                "fb_message":posted.get('message').get('text'),
                "fb_dump":data,
                "fb_from":posted.get('sender').get('id'),
                "fb_to":posted.get('recipient').get('id')
            }

            serializer = self.serializer_class(data=post)

            if serializer.is_valid():
                fb = Facebook.objects.create(**serializer.validated_data)
                
                self.send_to_helpline(fb)
                # res = self.send_to_facebook(posted)
                return True #  Response("Success", status=status.HTTP_200_OK)# Response(serializer.validated_data, status=status.HTTP_200_OK) #1_CREATED)
            else:
                return False

    def send_message(self,recipient_id, message):
        """Send a response to Facebook"""
        
        headers = {"access_token":settings.FB_TOKEN} 
        fburl = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s&recipient=3412749322156758' % settings.FB_TOKEN
        
        try:
            chat = {
                "recipient":{
                    "id":recipient_id
                },
                "messaging_type": "RESPONSE",
                "message":message
                }
            print("DATA: %s " % chat)
            response = requests.post(fburl, json=chat,headers=headers)
            json_response = response.json()
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print('Success!')
        return response.json()


    # SEND TO HELPLINE
    def send_to_helpline(self,chat_data):
        # send chat to helpline
        token = False
        try:

            headers = {
                "authorization":"Basic %s" % settings.HELPLINE_TOKEN,
                "accept": "*/*"
                }

            response = requests.post(settings.HELPLINE_BASE,headers=headers,verify=False)
            json_response = response.json()
            token = json_response["ss"][0][0]

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP token error: {http_err}')
        except Exception as err:
            print(f'Other token error occurred: {err}') 
        else:
            print('Token Success!')

        if token:
            try:
                
                tm = time.mktime(datetime.now().timetuple())
                chat = {
                    "channel":"chat",
                    "from":chat_data.fb_from,
                    "message":chat_data.fb_message,
                    "timestamp":tm,
                    "session_id":tm,
                    "message_id":chat_data.id,
                    "gateway_msg_id":4342
                }

                headers = {"Authorization":"Bearer %s" % token,'Content-Type':'application/json' }

                response = requests.post('%smsg/' % settings.HELPLINE_BASE, json=chat,headers=headers,verify=False)
                json_response = response.json()
                print("CHAT: %s:%s" %(response.status_code,json_response))
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP helpline chat error occurred: {http_err}')
            except Exception as err:
                print(f'Other helpline chat error occurred: {err}') 
            else:
                print('Success!')
    
    def send_to_facebook(self,chat_data):
        try:
            
            headers = {"access_token":"EAAq50PnynzgBAP6DPk5giqGSJo6TYNPcDlehl2WWGlf2vl0UvUcQiMNntECZBBekL381aGu1POPGUKJWU3hjg30PGFsYO8GFFsZAIewfCFIMD8Rwj61unfzhjIK5FUEeagZAWuGKh9D4oXeaQglZCP9K0fgK6xtLjzNyeXhHrcR8kNJY9hIeZC5mHH4ZBJJamfFrbjrsyrSAZDZD"}
            
            fburl = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAq50PnynzgBAP6DPk5giqGSJo6TYNPcDlehl2WWGlf2vl0UvUcQiMNntECZBBekL381aGu1POPGUKJWU3hjg30PGFsYO8GFFsZAIewfCFIMD8Rwj61unfzhjIK5FUEeagZAWuGKh9D4oXeaQglZCP9K0fgK6xtLjzNyeXhHrcR8kNJY9hIeZC5mHH4ZBJJamfFrbjrsyrSAZDZD&recipient=3412749322156758'
            
            if chat_data.get('message',False) and not chat_data.get('is_echo',False):
                message = chat_data.get('message') 
                if(message.get('quick_reply',False)):
                    message = self.getResponse(message.get('quick_reply').get('payload'))
                    # message = self.getResponse(pl)
                else:   
                    chat = {
                        "recipient": {
                        "id":chat_data.get('sender').get('id'), # "3412749322156758"
                        },
                        "message": {"text":"Ninafurahi kukukaribisha, naitwa  #Malezi. Mimi ni roboti  ya @SemaTanzania. Kwanza kabisa naomba tufahamiane. Kama hutojali nitakuuliza maswali mawiliili kuweza kukufahamu nakusaidia kuboresha huduma zetu."}
                    }
                    response = requests.post(fburl, json=chat,headers=headers)
                    message = {
                                "text":"Tafadhali chagua namba inayokutambulisha vyema zaidi:\n Je, jinsia yako ni: -", 
                                "quick_replies":[{
                                    "content_type":"text",
                                    "title":"01: Mwanamke",
                                    "payload":"MWANAMKE"
                                },{
                                    "content_type":"text",
                                    "title":"02: Mwanamme",
                                    "payload":"MWANAMKE"
                                },{
                                    "content_type":"text",
                                    "title":"03 Naomba nisijubu swali hili",
                                    "payload":"MWANAMKE"
                                }
                                ]
                            }
            else:
                message = {"text":"2:Ninafurahi kukukaribisha, naitwa  #Malezi. Mimi ni roboti  ya @SemaTanzania. Kwanza kabisa naomba tufahamiane. Kama hutojali nitakuuliza maswali mawiliili kuweza kukufahamu nakusaidia kuboresha huduma zetu."}
            
            chat = {
                "recipient":{
                    "id":chat_data.get('sender').get('id')
                },
                # "messaging_type": "RESPONSE",
                "message":message
                }
                
            response = requests.post(fburl, json=chat,headers=headers)
            json_response = response.json()
            print("THE MESSAGE: %s " % json_response)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print('Success!')

        return chat

class FacebookViewSetBot(viewsets.ViewSet):

    queryset = Facebook.objects.all().order_by('-id')
    serializer_class = FacebookSerializer
    
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = [permissions.IsAuthenticated]

    def list(self, request, format=None):
        """
        Return a list of all sources.
        """
        mode = request.GET.get('hub.mode',False)
        token = request.GET.get('hub.verify_token',False)
        challenge = request.GET.get('hub.challenge',False)

        if(mode and token):
            if mode == "subscribe" and token == 'aYyHMLNwmE)Y?-G};x)a2zt6wrl48gayahugfnlBx!Rfh%e&x':
                return Response(int(challenge),status=200)
            else:
                return Response(status=403)
        else:
            queryset = Facebook.objects.all().order_by('-id')
            serializer_class = FacebookSerializer(queryset, many=True)

            return Response(serializer_class.data)

    def create(self, request):
        if request.data.get('object') == 'page':
            posted = request.data.get('entry')[0].get('messaging')[0]
            response_message = "NO ACTION"

            if(posted.get('message',False)):
                message = posted.get('message')

                if not message.get('is_echo',False): # and message.get('text'):
                    recipient = posted.get('sender').get('id')
                    if (message.get('quick_reply',False)):
                        qreply = message.get('quick_reply')
                        response_message = self.handlePayload(qreply.get('payload'))
                        self.send_message(recipient,response_message)
                    elif (message.get('attachments',False)):
                        response_message = self.handleAttachmentMessage()
                    elif (message.get('text',False)):
                        response_message = self.handleTextMessage(request.data,posted)
                        
                        message = {"text":"Ninafurahi kukukaribisha, naitwa  #Malezi. Mimi ni roboti  ya @SemaTanzania. Kwanza kabisa naomba tufahamiane. Kama hutojali nitakuuliza maswali mawiliili kuweza kukufahamu nakusaidia kuboresha huduma zetu."}
                        
                        self.send_message(recipient, message)
                        response_message = self.handlePayload()
                        self.send_message(recipient, response_message)
            
                
            elif (posted.get('postback',False)):
                response_message = self.handlePostback()
            elif (posted.get('referral',False)):
                response_message = self.handleReferral()
            elif (posted.get('optin',False)):
                response_message = self.handleOptIn()
            elif (posted.get('pass_thread_control',False)):
                response_message = self.handlePassThreadControlHandover()

            return  Response(response_message, status=status.HTTP_200_OK)
                
        return Response({'status': 'Bad Request %s ' % request.data,
                         'message': "Could not process request"},
                          status=status.HTTP_400_BAD_REQUEST)
    def handleTextMessage(self,data,message):
        ret = self.saveItem(data,message)
    def saveItem(self,data,posted):
        
            post = {
                "fb_unique":posted.get('message').get('mid'),
                "fb_message":posted.get('message').get('text'),
                "fb_dump":data,
                "fb_from":posted.get('sender').get('id'),
                "fb_to":posted.get('recipient').get('id')
            }

            serializer = self.serializer_class(data=post)

            if serializer.is_valid():
                fb = Facebook.objects.create(**serializer.validated_data)
                
                # self.send_to_helpline(fb)
                # res = self.send_to_facebook(posted)
                return True #  Response("Success", status=status.HTTP_200_OK)# Response(serializer.validated_data, status=status.HTTP_200_OK) #1_CREATED)
            else:
                return False

    def handlePayload(self,payload=False):
        if not payload:
            payload = "WELCOME"
        else:
            payload = payload.upper()
        
        responses = {
            "WELCOME":{
                "text":"Tafadhali chagua namba inayokutambulisha vyema zaidi: \n Je, jinsia yako ni: -\n",
                "quick_replies":[{
                    "content_type":"text",
                    "title":"01. Mwanamke",
                    "payload":"UMRI"
                },{
                    "content_type":"text",
                    "title":"01",
                    "payload":"UMRI"
                }]
            },
            "UMRI":{
                "text":"Je, uko katika kundi gani la umri?"
                ,
                "quick_replies":[{
                    "content_type":"text",
                    "title":"04. Miaka 13 hadi 18",
                    "payload":"MIAKA1"
                },{
                    "content_type":"text",
                    "title":"05. Miaka 18 hadi 25",
                    "payload":"MIAKA2"
                },{
                    "content_type":"text",
                    "title":"06. Miaka 25 hadi 35",
                    "payload":"MIAKA3"
                },{
                    "content_type":"text",
                    "title":"07. Miaka 35 na zaidi",
                    "payload":"MIAKA4"
                }]
            }
        }

        return responses.get(payload)


    def send_message(self,recipient_id, message):
        """Send a response to Facebook"""
        
        headers = {"access_token":settings.FB_TOKEN} 
        fburl = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s&recipient=3412749322156758' % settings.FB_TOKEN
        
        try:
            chat = {
                "recipient":{
                    "id":recipient_id
                },
                "messaging_type": "RESPONSE",
                "message":message
                }
            print("DATA: %s " % chat)
            response = requests.post(fburl, json=chat,headers=headers)
            json_response = response.json()
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print('Success!')
        return response.json()


    # SEND TO HELPLINE
    def send_to_helpline(self,chat_data):
        # send chat to helpline
        token = False
        try:

            headers = {
                "authorization":"Basic %s" % settings.HELPLINE_TOKEN,
                "accept": "*/*"
                }

            response = requests.post(settings.HELPLINE_BASE,headers=headers,verify=False)
            json_response = response.json()
            token = json_response["ss"][0][0]

            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP token error: {http_err}')
        except Exception as err:
            print(f'Other token error occurred: {err}') 
        else:
            print('Token Success!')

        if token:
            try:
                
                tm = time.mktime(datetime.now().timetuple())
                chat = {
                    "channel":"chat",
                    "from":chat_data.fb_from,
                    "message":chat_data.fb_message,
                    "timestamp":tm,
                    "session_id":tm,
                    "message_id":chat_data.id,
                    "gateway_msg_id":4342
                }

                headers = {"Authorization":"Bearer %s" % token,'Content-Type':'application/json' }

                response = requests.post('%smsg/' % settings.HELPLINE_BASE, json=chat,headers=headers,verify=False)
                json_response = response.json()
                print("CHAT: %s:%s" %(response.status_code,json_response))
                # If the response was successful, no Exception will be raised
                response.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP helpline chat error occurred: {http_err}')
            except Exception as err:
                print(f'Other helpline chat error occurred: {err}') 
            else:
                print('Success!')
    
    def send_to_facebook(self,chat_data):
        try:
            
            headers = {"access_token":"EAAq50PnynzgBAP6DPk5giqGSJo6TYNPcDlehl2WWGlf2vl0UvUcQiMNntECZBBekL381aGu1POPGUKJWU3hjg30PGFsYO8GFFsZAIewfCFIMD8Rwj61unfzhjIK5FUEeagZAWuGKh9D4oXeaQglZCP9K0fgK6xtLjzNyeXhHrcR8kNJY9hIeZC5mHH4ZBJJamfFrbjrsyrSAZDZD"}
            
            fburl = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAq50PnynzgBAP6DPk5giqGSJo6TYNPcDlehl2WWGlf2vl0UvUcQiMNntECZBBekL381aGu1POPGUKJWU3hjg30PGFsYO8GFFsZAIewfCFIMD8Rwj61unfzhjIK5FUEeagZAWuGKh9D4oXeaQglZCP9K0fgK6xtLjzNyeXhHrcR8kNJY9hIeZC5mHH4ZBJJamfFrbjrsyrSAZDZD&recipient=3412749322156758'
            
            if chat_data.get('message',False) and not chat_data.get('is_echo',False):
                message = chat_data.get('message') 
                if(message.get('quick_reply',False)):
                    message = self.getResponse(message.get('quick_reply').get('payload'))
                    # message = self.getResponse(pl)
                else:   
                    chat = {
                        "recipient": {
                        "id":chat_data.get('sender').get('id'), # "3412749322156758"
                        },
                        "message": {"text":"Ninafurahi kukukaribisha, naitwa  #Malezi. Mimi ni roboti  ya @SemaTanzania. Kwanza kabisa naomba tufahamiane. Kama hutojali nitakuuliza maswali mawiliili kuweza kukufahamu nakusaidia kuboresha huduma zetu."}
                    }
                    response = requests.post(fburl, json=chat,headers=headers)
                    message = {
                                "text":"Tafadhali chagua namba inayokutambulisha vyema zaidi:\n Je, jinsia yako ni: -", 
                                "quick_replies":[{
                                    "content_type":"text",
                                    "title":"01: Mwanamke",
                                    "payload":"MWANAMKE"
                                },{
                                    "content_type":"text",
                                    "title":"02: Mwanamme",
                                    "payload":"MWANAMKE"
                                },{
                                    "content_type":"text",
                                    "title":"03 Naomba nisijubu swali hili",
                                    "payload":"MWANAMKE"
                                }
                                ]
                            }
            else:
                message = {"text":"2:Ninafurahi kukukaribisha, naitwa  #Malezi. Mimi ni roboti  ya @SemaTanzania. Kwanza kabisa naomba tufahamiane. Kama hutojali nitakuuliza maswali mawiliili kuweza kukufahamu nakusaidia kuboresha huduma zetu."}
            
            chat = {
                "recipient":{
                    "id":chat_data.get('sender').get('id')
                },
                # "messaging_type": "RESPONSE",
                "message":message
                }
                
            response = requests.post(fburl, json=chat,headers=headers)
            json_response = response.json()
            print("THE MESSAGE: %s " % json_response)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print('Success!')

        return chat


class TwitterViewSet(viewsets.ViewSet):

    queryset = Twitter.objects.all().order_by('-id')
    serializer_class = TwitterSerializer
    
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = [permissions.IsAuthenticated]

    def list(self, request, format=None):
        """
        Return a list of all sources.
        """
        mode = request.GET.get('hub.mode',False)
        token = request.GET.get('hub.verify_token',False)
        challenge = request.GET.get('hub.challenge',False)

        if(mode and token):
            if mode == "subscribe" and token == 'aYyHMLNwmE)Y?-G};x)a2zt6wrl48gayahugfnlBx!Rfh%e&x':
                return Response(int(challenge),status=200)
            else:
                return Response(status=403)
        else:
            queryset = Twitter.objects.all().order_by('-id')
            serializer_class = TwitterSerializer(queryset, many=True)

            return Response(serializer_class.data)

    def create(self, request):
        if request.data.get('object') == 'page':
            posted = request.data.get('entry')[0].get('messaging')[0]
            posted = {
                "tw_unique":posted.get('message').get('mid'),
                "tw_message":posted.get('message').get('text'),
                "tw_dump":request.data,
                "tw_from":posted.get('sender').get('id'),
                "tw_to":posted.get('recipient').get('id')
            }

            # {'object': 'page', 'entry': [{'id': '379177569599649', 'time': 1662798923038, 'messaging': [{'sender': {'id': '3412749322156758'}, 'recipient': {'id': '379177569599649'}, 'timestamp': 1662795371999, 'message': {'mid': 'm_NEf-F398IC5LSB1kVK15fjw9B9-lqkmk2Y-ySamD-Prqj1PJ5wVhwwf7Xg0BwqP8D6BGM5-mZ9BfduKDjTAApw', 'text': 'Sisi ndio hao', 'nlp': {'intents': [], 'entities': {}, 'traits': {'witgreetings': [{'id': '5900cc2d-41b7-45b2-b21f-b950d3ae3c5c', 'value': 'true', 'confidence': 0.8493}]}, 'detected_locales': [{'locale': 'sw_KE', 'confidence': 1}]}}}]}]} 
            serializer = self.serializer_class(data=posted)

            if serializer.is_valid():
                fb = Twitter.objects.create(**serializer.validated_data)
                
                self.send_to_helpline(fb)


            return Response(serializer.validated_data, status=status.HTTP_200_OK) #1_CREATED)

        return Response({'status': 'Bad Request %s ' % request.data,
                         'message': "Could not process request"},
                          status=status.HTTP_400_BAD_REQUEST)

