import datetime
import locale,random,string
from django.contrib.sessions.models import Session
from django.utils import timezone

QUEUE_STATUS = {"0":"OFFLINE","1":"AVAILABLE","2":"ON BREAK","3":"PERSONAL BREAK","4":"COACHING AND TRAINING"}
TYPE_CHOICES = [("userpass","Password")]
PERSON_TYPE = [("REPORTER","REPORTER"),("CLIENT","CLIENT"),("PERPETRATOR","PERPETRATOR")]
CHAT_SOURCES = [("WENI","WENI"),("HELPLINE","HELPLINE")]
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

RELATIONSHIP_CHOICES = [
                    ("Father","Father"),
                    ("Mother","Mother"),
                    ("Sister","Sister"),
                    ("Brother","Brother"),
                    ("Grandfather","Grandfather"),
                    ("Grandmother","Grandmother"),
                    ("Uncle","Uncle"),
                    ("Aunt","Aunt"),
                    ("Cousin","Cousin"),
                    ("Other family member","Other family member"),
                    ("Foster Father","Foster Father"),
                    ("Foster Mother","Foster Mother"),
                    ("Stepfather","Stepfather"),
                    ("Stepmother","Stepmother"),
                    ("Step brother","Step brother"),
                    ("Step sister","Step sister"),
                    ("Teacher","Teacher"),
                    ("Worker in care facility","Worker in care facility"),
                    ("Friend of the child","Friend of the child"),
                    ("Peer/ Not a friend","Peer/ Not a friend"),
                    ("Other not related adult","Other not related adult"),
                    ("Nanny/House help","Nanny/House help"),
                    ("Neighbor","Neighbor"),
                    ("Unknown","Unknown")
                ]
DISPOSITIONS = {
    # "1":"Blank",
    # "2":"Prank",
    "3":"Abusive Caller",
    "4":"Appreciation",
    # "5":"Complaint",
    "6":"Completed",
    "7":"Dropped",
    "8":"Feedback",
    # "9":"Greeting",
    # "10":"Inquiry",
    "11":"Insufficient Information",
    "12":"Mistake",
    "13":"Testing Line",
    "14":"Silent"
}


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
AREA_CHOICES = {
    "19":"Account Management",
    "31":"BAT",
    "3":"DGIE",
    "1":"DGIE - Visa on arrival and overstay penalties",
    "2":"HEC",
    "23":"IECMS",
    "4":"MHC",
    "15":"MINALOC",
    "14":"MINIJUST-GAZETTE",
    "10":"MUSEUM",
    "16":"NIDA",
    "7":"NOTARY",
    "12":"NPPA",
    "5":"Payment Experience",
    "8":"RBC",
    "24":"RDB",
    "9":"REB",
    "13":"RGB",
    "25":"RHA",
    "17":"RLMUA",
    "6":"RNP",
    "18":"RSSB",
    "11":"RURA",
    "29":"N/A",
    "36":"IremboGov not accessible",
    "37":"IremboGov loading endlessly"
}

CF_CHOICES = ["Complain","Query","Request for application","N/A"] #,"Praise","Suggestion",
REQUESTER_CHOICES = ["Agent","Citizen","Government Officer","Irembo staff"]

def weekdays(weekday='Monday'):
    current_locale = locale.getlocale()
    if current_locale not in weekdays._days_cache:
        # Add day names from a reference date, Monday 2001-Jan-1 to cache.
        weekdays._days_cache[current_locale] = [
            datetime.date(2001, 1, i).strftime('%A') for i in range(1, 8)]
    days = weekdays._days_cache[current_locale]
    index = days.index(weekday)
    return days[index:] + days[:index]

weekdays._days_cache = {}  # initialize cache

def defaultdict():
    return {'accept_list': [], 'reject_list': []}
    
def weekdates():
    week_day=datetime.datetime.now().isocalendar()[2]
    
    start_date=datetime.datetime.now() - datetime.timedelta(days=week_day-1)
    
    dates=[str((start_date + datetime.timedelta(days=i)).date()) for i in range(7)]
    return dates

def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return uid_list
    #return User.objects.filter(id__in=uid_list)

def getRandomString(N=10):
    ran_str = ''.join(random.choices(string.ascii_uppercase +
                            string.digits, k = N))