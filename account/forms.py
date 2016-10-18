from django import forms
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
# this allows links in validation error messages
from django.utils.safestring import mark_safe

class AccountSettingsForm(forms.Form):
    
    # this allows us to access the request variable
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        # make sure passwords match
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
    
        # check if email is already being used
        get_email = self.cleaned_data.get('email')
        # hidden username is used just in case the username is updated and this will prevent the query from not working
        username = self.cleaned_data.get('hidden_username')
        user = User.objects.get(username=username)
        email_exists = User.objects.filter(email=get_email)
        if get_email != user.email:
            if email_exists and not self.request:
                raise forms.ValidationError(mark_safe("The email address is already used by another account."))
    
        return self.cleaned_data
    
    email = forms.EmailField(label='Email Address')
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(render_value=True), required=False, validators=[MinLengthValidator(8)])
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(render_value=True), required=False, validators=[MinLengthValidator(8)])
    emailUpdates = forms.BooleanField(label='Receive Email Updates', widget=forms.CheckboxInput, required=False)    
    hidden_username = forms.CharField(widget=forms.HiddenInput)
    
class RegisterForm(forms.Form):
    
    def clean(self):
        password = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('confirmPassword')
        
        # if firstname and lastName fields are not empty, combine for username and check if username exists
        if self.cleaned_data.get('firstName') and self.cleaned_data.get('lastName'):
            username = self.cleaned_data.get('firstName') + '.' + self.cleaned_data.get('lastName')
            user = User.objects.filter(username=username)
            if user:
                raise forms.ValidationError("The username %s is already in use." % username)
        
        # check if email is already being used
        email = self.cleaned_data.get('email')
        email = User.objects.filter(email=email)
        if email:
            raise forms.ValidationError(mark_safe("The email address is already used by another account. If you've already created an account you can reset your password by <a href='/forgot'>clicking here</a>."))
        
        # if passwords do not match raise error
        if password and password != confirmPassword:
            raise forms.ValidationError('Passwords do not match.')
    
        return self.cleaned_data
    
    firstName = forms.CharField(label='First Name')
    lastName = forms.CharField(label='Last Name')
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirmPassword = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
class ForgotPassForm(forms.Form):
    
    email = forms.EmailField(label='Email Address')
    
class ResetPassForm(forms.Form):

    def clean(self):
        password = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('confirmPassword')
        
        # if passwords do not match raise error
        if password and password != confirmPassword:
            raise forms.ValidationError('Passwords do not match.')
        
        return self.cleaned_data
        
    password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirmPassword = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

class CreateUserForm(forms.Form):
    
    def clean(self):
                # if firstname and lastName fields are not empty, combine for username and check if username exists
        if self.cleaned_data.get('firstName') and self.cleaned_data.get('lastName'):
            username = self.cleaned_data.get('firstName') + '.' + self.cleaned_data.get('lastName')
            user = User.objects.filter(username=username)
            if user:
                raise forms.ValidationError("The username %s is already in use." % username)
        
        # check if email is already being used
        email = self.cleaned_data.get('email')
        email = User.objects.filter(email=email)
        if email:
            raise forms.ValidationError(mark_safe("The email address is already used by another account."))
    
        return self.cleaned_data
    
    ACCOUNT_TYPE_CHOICES = (
        ('user', "User"),
        ('appraiser', "Appraiser")
    )
    
    firstName = forms.CharField(label='First Name')
    lastName = forms.CharField(label='Last Name')
    email = forms.EmailField(label='Email Address')
    accountType = forms.ChoiceField(label='Account Type', choices=ACCOUNT_TYPE_CHOICES)
    
class EditUserForm(forms.Form):
    
    # this allows us to access the request variable
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EditUserForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        # make sure passwords match
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        # check if email is already being used
        get_email = self.cleaned_data.get('email')
        # hidden username is used just in case the username is updated and this will prevent the query from not working
        username = self.cleaned_data.get('hidden_username')
        user = User.objects.get(username=username)
        email_exists = User.objects.filter(email=get_email)
        if get_email != user.email:
            if email_exists and not self.request:
                raise forms.ValidationError(mark_safe("The email address is already used by another account."))
    
        return self.cleaned_data
    
    ACCOUNT_TYPE_CHOICES = (
        ('user', "User"),
        ('appraiser', "Appraiser")
    )
    
    username = forms.CharField(label="Username")
    firstName = forms.CharField(label="First Name")
    lastName = forms.CharField(label="Last Name")
    email = forms.EmailField(label='Email Address')
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(render_value=True), required=False, validators=[MinLengthValidator(8)])
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(render_value=True), required=False, validators=[MinLengthValidator(8)])
    accountType = forms.ChoiceField(label='Account Type', choices=ACCOUNT_TYPE_CHOICES)
    emailUpdates = forms.BooleanField(label='Receive Email Updates', widget=forms.CheckboxInput, required=False)
    hidden_username = forms.CharField(widget=forms.HiddenInput)