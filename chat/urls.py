from django.urls import path
from . import views
app_name = 'chat'
urlpatterns = [
    path('', views.index, name='index'),
    path('room-detail/<str:room_name>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create-room'),
    path('private-room/<str:username>/',views.private_room,name='private-room'),
]
