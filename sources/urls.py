from django.urls import path,include
from sources import views

urlpatterns = [
    # path('',include(router.urls)),
    path(r'sms', views.sms,name='sms'),
    path(r'email', views.email,name='email'),
    path(r'facebook', views.facebook,name='facebook'),
    path(r'twitter', views.twitter,name='twitter'),
    path(r'whatsapp', views.whatsapp,name='whatsapp'),
    path(r'telegram', views.telegram,name='telegram'),
]
