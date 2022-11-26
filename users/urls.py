from django.urls import path,include
from users import views

urlpatterns = [
    path('',views.users,name='users'),
    
    path('<int:userid>/',views.users,name='viewuser'),
    path('<int:userid>/<str:action>/',views.users,name='edituser'),
    path('register/',views.users,name='register'),

    path('roles',views.roles,name='roles'),
    path('roles/<int:roleid>/',views.users,name='viewrole'),
    path('roles/<int:roleid>/edit/',views.users,name='editrole'),

]
