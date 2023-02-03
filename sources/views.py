from email import message
from sources.models import Telegram
from django.shortcuts import render
from sources.models import SMS, Facebook, Twitter, Emails, Whatsapp, Telegram
from django.contrib.auth.decorators import login_required
import imaplib as imap
import email as imail
from datetime import datetime

# Create your views here.

@login_required
def sms(request,smsid=False):
    data = {
        "title":"SMS Details"
    }

    if(request.method == 'POST'):
        try:
            sms = SMS()

            sms.sms_sender = 705969166
            sms.sms_receiver = request.POST.get('receiver')
            sms.sms_message = request.POST.get('message')

            sms.save()
            data['message'] = "SMS saved successfully"

        except Exception as e:
            data['message'] = "Could not save message %s " % str(e.args[0])
    
    if smsid:
        data['sms'] = SMS.objects.get(pk=smsid).order_by('-id')
    else:
        data['smss'] = SMS.objects.all().order_by('-id')

    return render(request, 'sources/sms.html',data)



@login_required
def syncemail(request):
    res = {}
    try:
        con = imap.IMAP4_SSL("mail.nenyon.com",993)
    
        con.login("kazi@nenyon.com","4K(XlpPqNiD9")

        con.select("INBOX")
        res['status'], data = con.search(None, 'ALL')

        mails = []
        
        for num in  data[0].split():
            mail = {}
            typ, maildata = con.fetch(num,'(RFC822)') #'(UID BODY[TEXT])')
            
            # Parse the email
            raw = maildata[0][1]
            full_mail =  imail.message_from_bytes(raw)
            
            # Body details
            _from = full_mail['from'].split("<")
            mail['ide'] = int(num)
            mail['from_name'] = _from[0]
            mail['from_mail'] = _from[1][:-1]
            mail['to'] = full_mail['to']
            mail['cc'] = full_mail['cc'] if full_mail['cc'] else ""
            mail['bcc'] = full_mail['bcc'] if full_mail['bcc'] else ""
            mail['subject'] = full_mail['subject']
            mail['date'] = full_mail['date'] #datetime.strptime(str(full_mail['date']), "%Y-%m-%d %H:%M:%S") 
            files = []

            for part in full_mail.walk():
                maintype = part.get_content_maintype()
                diposition = part.get('Content-Disposition')
                if part.get_content_type() == "text/html":
                    body = part.get_payload(decode=True)
                    mail['body'] = body.decode('utf-8')

                if maintype != 'multipart' and diposition is not None:
                    
                    outputdir = "main/static/dist/files/"
                    open(outputdir + '/' + part.get_filename(), 'wb').write(part.get_payload(decode=True))
                    files.append(part.get_filename())
            mail['files'] = files
            mails.append(mail)
        res['mails'] = mails
    except Exception as e:
            res['message'] = "Could not retrieve emails %s " % e
    return res

@login_required
def email(request):
    data = {"title":"Email Records"}
    data['emails'] = syncemail(request)

    return render(request,'sources/email.html',data)

@login_required
def facebook(request):
    data = {"title":"Facebook Records"}
    data['fbs'] = Facebook.objects.all()
    return render(request,'sources/facebook.html',data)

@login_required
def twitter(request):
    data = {"title":"Twitter Records"}
    data['tweets'] = Twitter.objects.all()
    return render(request,'sources/twitter.html',data)

@login_required
def whatsapp(request):
    data = {"title":"Whatsapp Records"}
    data['wts'] = Whatsapp.objects.all()
    return render(request,'sources/whatsapp.html',data)

@login_required
def telegram(request):
    data = {"title":"Telegram Records"}
    data['teles'] = Telegram.objects.all()
    return render(request,'sources/telegram.html',data)

