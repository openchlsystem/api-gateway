import datetime
import locale,random,string
from django.utils import timezone


CHAT_SOURCES = [("WENI","WENI"),("INBOX","INBOX"),("OUTBOX","OUTBOX")]
CHAT_CHANNELS = [("WENI","WENI"),("FACEBOOK","FACEBOOK"),("WHATSAPP","WHATSAPP")]
MARITAL_CHOICES = [
                    ("Single","Single"),
                    ("Married","Married"),
                    ("Separated","Separated"),
                    ("Single Parent","Single Parent"),
                    ("Widower","Widower"),
                    ("Widow","Widow")
                ]
PERSON_STATUS_CHOICES = [
                    ("Active","Active"),
                    ("Domant","Domant"),
                    ("Deactivated","Deactivated"),
                    ("Deleted","Deleted")
                ]
GENDER_CHOICES = [
                    ("Male","Male"),
                    ("Female","Female")
                ]

STATUS_CHOICES = {
                    "2":"Open",
                    "3":"Pending",
                    "4":"Resolved",
                    "5":"Closed",
                    "6":"Waiting on Customer",
                    "7":"Witing on Third Party"
                }
PRIORITY_CHOICES = {
                        "1":"Low",
                        "2":"Medium",
                        "3":"High",
                        "4":"Urgent"
                    }


def defaultdict():
    return {'accept_list': [], 'reject_list': []}
    
def getRandomString(N=10):
    ran_str = ''.join(random.choices(string.ascii_uppercase +
                            string.digits, k = N))
    return ran_str