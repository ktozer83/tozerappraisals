from django import forms
from django.core.validators import MinLengthValidator
import re

class OrderForm(forms.Form):
    
    def clean(self):
        contactNum = self.cleaned_data.get('contactNum')
        
        if self.cleaned_data.get('contactNum'):
            for char in contactNum:
                if not char in '1234567890()-':
                    raise forms.ValidationError("Invalid contact number. Please enter again.")
                
            strip_contactNum = re.compile(r'[^\d]+')
            contactNum = strip_contactNum.sub('', contactNum)
            if len(contactNum) > 10:
                raise forms.ValidationError("Contact number is too long. Please enter again.")
            elif len(contactNum) < 10:
                raise forms.ValidationError("Contact number is too short. Please enter again.")
            
        return self.cleaned_data
    
    APP_TYPE_CHOICES = (
        ('', 'Please Choose'),
        ('Full Appraisal', 'Full Appraisal'),
        ('Drive By', 'Drive By'),
        ('Progess Report', 'Progess Report'),
        ('Desktop', 'Desktop')
    )
    
    applicantName = forms.CharField(label='Applicant Name',widget=forms.TextInput(attrs={'maxlength':225}))
    address = forms.CharField(label='Address',widget=forms.TextInput(attrs={'maxlength':225}))
    city = forms.CharField(label='City',widget=forms.TextInput(attrs={'maxlength':225}))
    contactNum = forms.CharField(label='Contact Number',widget=forms.TextInput(attrs={'maxlength':13}))
    dueDate = forms.CharField(label='Due Date',widget=forms.TextInput(attrs={'maxlength':10}))
    appType = forms.ChoiceField(label='Appraisal Type', choices=APP_TYPE_CHOICES)
    
class DeleteOrderForm(forms.Form):
    
    deleteOrderConfirm = forms.CharField(label="",widget=forms.TextInput(attrs={'maxlength':5}))
    
class EditMessageForm(forms.Form):
    
    def clean(self):
        return self.cleaned_data
    
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs={'maxlength':500}))
    
class GotoOrderForm(forms.Form):
    
    def clean(self):
        goto_order = self.cleaned_data.get('goto_order')
        
        # make sure only numbers are entered
        if goto_order:
            for char in goto_order:
                if not char in '1234567890':
                    raise forms.ValidationError("Please enter numbers only.")
        
        return self.cleaned_data
    
    goto_order = forms.CharField(label="Order", widget=forms.TextInput(attrs={'maxlength':5}))

class UploadReportForm(forms.Form):
    
    def clean(self):
        ext = '.pdf'
        if not ext in self.cleaned_data['file'].name:
            raise forms.ValidationError("File must be pdf.")
        
        return self.cleaned_data
    
    file = forms.FileField()