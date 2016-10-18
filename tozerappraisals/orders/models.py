from django.db import models
import datetime
from django.utils import timezone

# Create your models here.
class Order(models.Model):

    class Meta:
        permissions = (
            ("view_all_orders","Can view all orders"),
            ("view_any_order", "Can view any order"),
        )

    APP_TYPE_CHOICES = (
        ('Desktop', 'Desktop'),
        ('Drive By', 'Drive By'),
        ('Full Appraisal', 'Full Appraisal'),
        ('Progess Report', 'Progess Report')
    )
    orderID = models.AutoField(primary_key=True, max_length=11)
    viewed = models.IntegerField(max_length=1, default=0)
    applicantName = models.CharField(max_length=255)
    address = models.CharField(max_length=225)
    city = models.CharField(max_length=225)
    contactNum = models.CharField(max_length=13)
    dueDate = models.CharField(max_length=10, default='')
    appType = models.CharField(max_length=14,
                               choices=APP_TYPE_CHOICES,
                               default='Desktop')
    comments = models.CharField(max_length=500)
    username = models.CharField(max_length=255)
    contacted = models.IntegerField(max_length=1, default=0)
    status = models.IntegerField(max_length=1, default=0)
    inspectionDate = models.CharField(max_length=25, default='')
    orderDate = models.DateTimeField(auto_now=False, auto_now_add=False)
    updated = models.IntegerField(max_length=1, default=0)
    archive = models.IntegerField(max_length=1, default=0)
    
    def __unicode__(self):
        return self.orderID, self.applicantName, self.contactNum,
        self.address, self.city, self.appType, self.dueDate,
        self.comments, self.orderDate
        
class Comment(models.Model):
    commentID = models.AutoField(max_length=11, primary_key=True)
    orderNumber = models.ForeignKey(Order, db_column='orderNumber')
    username = models.CharField(max_length=255)
    comment = models.CharField(max_length=500)
    commentDate = models.DateTimeField(auto_now=False, auto_now_add=False)
    
    def __unicode__(self):
        return self.orderNumber, self.user, self.comment, self.commentDate

class Update(models.Model):
    updateID = models.AutoField(max_length=11, primary_key=True)
    orderNumber = models.ForeignKey(Order)
    update = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    updateDate = models.DateTimeField(auto_now=False, auto_now_add=False)
    
    def __unicode__(self):
        return self.orderNumber, self.update, self.username, self.updateDate

class WelcomeMessage(models.Model):
    message = models.CharField(max_length=500)
    last_updated = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=255)
        
class UploadReport(models.Model):
    id = models.AutoField(max_length=11, primary_key=True)
    filename = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    uploadDate = models.DateTimeField(auto_now=False, auto_now_add=False)
    
    def __unicode__(self):
        return self.id, self.file, self.username, self.uploadDate