
from django.urls import include, path
from rest_framework import routers
from api import views
from rest_framework.authtoken import views as v1

router = routers.DefaultRouter()
router.register(r'sources', views.SourcesViewSet,basename='feedback')
router.register(r'web', views.WebViewSet,basename='web')
router.register(r'chat', views.ChatViewSet,basename='Chat')
router.register(r'sms', views.SmsViewSet,basename='sms')
router.register(r'sms/(?P<pk>\w+)', views.SmsViewSet,basename='singlesms')
router.register(r'contacts', views.ContactsViewSet,basename='contacts')
router.register(r'contacts/(?P<pk>\w+)', views.ContactsViewSet,basename='singlecontact')
router.register(r'conversations', views.ConversationsViewSet,basename='conversations')
router.register(r'conversations/(?P<pk>\w+)', views.ConversationsViewSet,basename='singleconversation')
router.register(r'chat/(?P<sessionid>\w+)/close', views.ChatViewSet,basename='CloseChat')
router.register(r'twitter', views.TwitterViewSet,basename='Twitter')
router.register(r'facebook', views.FacebookViewSet,basename='Facebook')
router.register(r'whatsapp', views.WhatsAppViewSet,basename='Whatsapp')
router.register(r'safepal', views.SafePalViewSet,basename='safepal')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('token/', v1.obtain_auth_token),
#    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
