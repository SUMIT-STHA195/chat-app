from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Room(models.Model):
    room_name=models.CharField(max_length=50)
    members=models.ManyToManyField(User, related_name='members')
    is_group=models.BooleanField(default=True)
    admin=models.ForeignKey(User, blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.room_name

class Message(models.Model):
    content=models.TextField()
    room=models.ForeignKey(Room,on_delete=models.CASCADE, related_name='messages')
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user')
    timestamp=models.DateTimeField(default=timezone.now())

    class Meta:
        ordering=['timestamp']
    
    

