from datetime import datetime

from django.http import JsonResponse
from users.models import LogEntries, Roles,User
from django.contrib.auth.models import Group,Permission
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.apps import apps
from holla import settings as this
from django.template.defaulttags import register
from urllib.parse import quote
from django.db.models import F

from django.contrib.contenttypes.models import ContentType
# Create your views here.

@login_required
def roles(request,roleid=False,action=False):
    """
    API endpoint that allows users to be viewed or edited.
    """
    data = {"message":False,"title":"Role List"}

    # check if user submitted details
    if request.method == 'POST' and not action:
        try:
            role = Roles()
            role.role_name = request.POST.get('role_name')
            role.role_description = request.POST.get('role_desc')
            role.save()

            data["message"] = "Role created successfully"
            
        except Exception as e:
             data["message"] = "Could not create role %s " % e

    template = 'users/roles.html'

    if(roleid):
        data["roles"] = Roles.objects.get(pk=roleid)
    else:
        data["roles"] = Roles.objects.all().order_by('-id')

    return render(request,template ,data)

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary,dict):
        return dictionary.get(key)
    else:
        return key
@login_required
def users(request,userid=False,action=False):
    """
    API endpoint that allows users to be viewed or edited.
    """
    data = {'title':"User List",'message':False,"status":"success"}
    messages = {'passwordreset':"Could not reset password, try again","edit":"User edit failed,try agaian","changepassword":"Password change failed,try again"}
    # check if user submitted details
    
    if request.method == 'POST':
        try:
            if action == 'resetpassword':
                try:
                    usr =  User.objects.get(pk=userid)
                    usr.set_password(usr.username)
                    usr.save()
                    code = 200
                    data["message"] = "Password reset successful."
                except Exception as e:
                    code = 500
                    data["message"] = "Could not reset password, try again"
                
                response = JsonResponse(data)
                response.status_code = code
                return response

            if action == 'disable' or action == 'enable':
                try:
                    status = True if action == 'enable' else False
                    usr =  User.objects.get(pk=userid)
                    usr.is_active = status
                    usr.save()
                    code = 200
                    data["message"] = "User %sd successfully." % action
                except Exception as e:
                    code = 500
                    data["message"] = "Could not %s user, try again" % action
                
                response = JsonResponse(data)
                response.status_code = code
                return response
            

            if action == 'changepassword':
                # usr =  User.objects.get(pk=userid)
                usr = request.user
                usr.set_password(request.POST.get("passwd"))
                usr.save()
                
                return JsonResponse({"status":True,"message":"Password reset successfully"})

            if action and action == 'edit':
                usr =  User.objects.get(pk=userid)
            else:
                usr = User()
                usr.username = request.POST.get("username")
                usr.set_password(usr.username)
                usr.offdays = 0

            usr.firstname = request.POST.get("firstname") 
            usr.lastname  = request.POST.get("lastname")
            usr.email  = request.POST.get("email")
            usr.address  = "N/A" # request.POST.get("address")
            # usr.date_of_birth = datetime.now()
            # usr.location  = Locations.objects.get(request.POST.get("location"))
            usr.role = Roles.objects.get(pk=request.POST.get("role"))
            usr.avatar = request.POST.get("fl_avatar")
            usr.fresh_api = request.POST.get("service_key")
            usr.can_login = True
            usr.is_admin = True
            # usr.endpoint = endpoint

            usr.save()
            
            data["message"] = "User created successfully"
            code = 201

        except Exception as e:
            data["message"] = "User creation failed %s " % e.args[0]
            data["status"] = "error"
            # if action:
            #     data["message"] = messages[action]
            code = 500
        
        
        if action and action == 'edit':
            response = JsonResponse(data)
            response.status_code = code
            return response
        
    else:
        if action == "edit": 
            data["roles"] = Roles.objects.all().order_by('-id')
            data["user"] = get_object_or_404(User,pk=userid)
            return render(request,'users/edit.html' ,data)
        # else:
        #     user = get_object_or_404(User,pk=userid)
        #     return JsonResponse(user.is_active,safe=False)
    template = 'users/users.html'
    data["roles"] = Roles.objects.all().order_by('-id')
    if(userid and not action):
        data["users"] = User.objects.get(pk=userid) #.annotate(lastactivity=LogEntries.objects.filter(log_user_id=F('id')).last())
        template = 'main/profile.html'
        data["title"] = 'User Profile'
    else:
        data["users"] = User.objects.all().order_by('-id') #.annotate(lastactivity=LogEntries.objects.filter(log_user_id=F('id')).last()).order_by('-id')
        data['logged'] = User.objects.filter(id__in=HC.get_all_logged_in_users()) #.annotate(lastactivity=LogEntries.objects.filter(log_user_id=F('id')).last())
    return render(request,template ,data)
