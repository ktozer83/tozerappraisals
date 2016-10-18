from django import forms
from django.core.mail import send_mail

class ContactForm(forms.Form):
    name = forms.CharField(label='Your Name')
    email = forms.EmailField(label="Your Email")
    message = forms.CharField(widget=forms.Textarea, label="Your Comments/Questions")
    
    def send_email(self):
        pass
