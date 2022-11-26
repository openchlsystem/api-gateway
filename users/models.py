from email.policy import default
from statistics import mode
from time import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from datetime import datetime

# Create your models here.

class Roles(models.Model):
    role_name = models.CharField(max_length=100)
    role_description = models.CharField(max_length=200, blank=True)
    role_date = models.DateTimeField(auto_now_add=True)
    role_udate = models.DateTimeField(auto_now=True)

class UserManager(BaseUserManager):
    def create_user(self, email,username, password=None,**extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username,password=None,**extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            username,
            password,
            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    firstname = models.CharField(max_length=100, blank=False)
    lastname = models.CharField(max_length=100, blank=False)
    username = models.CharField(max_length=40, unique=True)
    phone = models.CharField(max_length=20, blank=False)
    #location = models.ForeignKey(Locations,related_name='_ulocation',null=True,on_delete=models.RESTRICT)
    address = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, blank=True)
    can_login = models.BooleanField(default=True)
    role = models.ForeignKey(Roles,related_name="role",on_delete=models.RESTRICT,default=1)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    #queue_status = models.CharField(max_length=100,default="OFFLINE", blank=False)
    #fresh_api = models.CharField(max_length=100,default="dnQ0YkJDRGtYOHA2c0ZTZ2M0TTpY", blank=False)
    # service = models.CharField(max_length=100,default="Other Services", blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    #endpoint = models.ForeignKey('calls.Endpoints',related_name="extension",on_delete=models.CASCADE,null=True)
    #lastcalltime = models.DateTimeField(null=True)
    #offdays = models.JSONField() 
    #lastevent = models.CharField(max_length=100,blank=True,default="")
    #lastlogin = models.DateTimeField(blank=True,null=True)
    #lastlogout = models.DateTimeField(blank=True,null=True)
    # logintime = models.IntegerField(default=0)
    # breaktime = models.IntegerField(default=0)
    # logintime = models.IntegerField(default=0)
    
    objects = UserManager()

    USERNAME_FIELD = 'email' #'username' 
    REQUIRED_FIELDS = ['firstname','lastname','username','role']

    def __str__(self):
        return self.firstname + " " + self.lastname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

# log entries
class LogEntries(models.Model):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    log_user = models.ForeignKey(User,related_name="log_user",on_delete=models.CASCADE,null=True)
    username = models.CharField(max_length=256, null=True)
    actiontime = models.DateTimeField(auto_now_add=True)
    timeinterval = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return '{0} - {1} - {2}'.format(str(self.action), self.username, self.ip)

    def __str__(self):
        return '{0} - {1} - {2}'.format(str(self.action), self.username, self.ip)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    LogEntries.objects.create(action='user_loggin', ip=ip,log_user=user, username=user.username)

    # user.lastevent = str("Login Event")
    user.lastlogin = datetime.now()
    user.save()


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    LogEntries.objects.create(action='user_loggout', ip=ip,log_user=user, username=user.username)
    # user.lastevent = 'Logout'
    user.lastlogout = datetime.now()
    user.save()


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    LogEntries.objects.create(action='user_loginfailed', username=credentials.get('username', None))
