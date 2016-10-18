from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    #required field
    user = models.OneToOneField(User)
    
    #other fields
    approved = models.IntegerField(default=False)
    change_password = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    get_email = models.BooleanField(default=True)

class ForgotPass(models.Model):
    token = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255)
    date = models.DateTimeField(auto_now=False)
    expirydate = models.DateTimeField(auto_now=False)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
post_save.connect(create_user_profile, sender=User)    