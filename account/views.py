from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from account.forms import AccountSettingsForm, RegisterForm, ForgotPassForm, ResetPassForm, CreateUserForm, EditUserForm
from tozerappraisals.orders.forms import DeleteOrderForm
from django.core.mail import send_mail, BadHeaderError
# import pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# cryptographic signing
from django.core.signing import Signer
# import forgot password model
from account.models import ForgotPass
# import datetime
import datetime
# this allows links in messages
from django.utils.safestring import mark_safe

from django.core.urlresolvers import reverse

# used for generating random string
import random
import string

# Create your views here.
class AccountView(FormView):
    template_name = 'account/account_overview.html'
    title = 'Account Settings'
    form_class = AccountSettingsForm
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username__exact=request.user.username)
        user_profile = self.request.user.get_profile()
        form = self.form_class
        context = super(AccountView, self).get_context_data()
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'account'
        context['settings_form'] = form({
            'email': user.email,
            'emailUpdates': user_profile.get_email,
            'hidden_username': user.username
        }, request=request)
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        self.success_url = '/account'
        user = User.objects.get(username__exact=self.request.user.username)
        user_profile = self.request.user.get_profile()
        user.email = self.request.POST['email']
        if self.request.POST['new_password']:
            user.set_password(self.request.POST['new_password'])
            # if the user was forced to change password, make sure once it is changed that they have access to the site
            if user_profile.change_password == 1:
                user_profile.change_password = 0
                user_profile.save()
        emailUpdates = 0
        if self.request.POST.get and 'emailUpdates' in self.request.POST and self.request.POST['emailUpdates'] == "on":
            emailUpdates = 1
            
        user_profile.get_email = emailUpdates
        
        user_profile.save()
        user.save()
        
        messages.success(self.request, 'Account Updated!')
        
        return super(AccountView, self).form_valid(form)
        
    def form_invalid(self, form):
        context = super(AccountView, self).get_context_data()
        context['settings_form'] = form
        context['page_title'] = self.title
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'account'
        
        return self.render_to_response(context)
    
class LoginView(FormView):
    template_name = 'account/login.html'
    title = 'Login'
    form_class = AuthenticationForm
    
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(reverse('orders:OrdersIndex'))
        else:
            form = self.form_class
            context = super(LoginView, self).get_context_data()
            context['login_form'] = form
            context['page_title'] = self.title
            
            return self.render_to_response(context)
        
    def form_valid(self, form):
        if self.request.GET.get('next'):
            self.success_url = self.request.GET.get('next')
        else:
            self.success_url = '/orders/'
        # get the user profile and see if user is blocked
        # if the user is blocked then do not log the user in and redirect to home page with error message
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password'])
        user_profile = user.get_profile()
        if user_profile.approved == 2:
            messages.error(self.request, "This account has been blocked and cannot access the site.")
            return redirect(reverse('home'))
        else:
            # if remember me is not checked then don't set a session cookie
            rememberMe = self.request.POST.get('rememberMe', False)
            if not rememberMe:
                self.request.session.set_expiry(0)
            login(self.request, user)
            messages.success(self.request, 'Thank you for logging in %s!' % user.username)
            return super(LoginView, self).form_valid(form)
    
    def form_invalid(self, form):
        context = super(LoginView, self).get_context_data()
        context['login_form'] = form
        context['page_title'] = self.title
        
        return self.render_to_response(context)

class LogoutView(View):
        
    def get(self, request):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('/')
        
class RegisterView(FormView):
    template_name = 'account/register.html'
    title = 'Register'
    form_class = RegisterForm
    success_url = '/orders/'
    
    def get_context_data(self, form):
        context = super(RegisterView, self).get_context_data()
        context['register_form'] = form
        context['page_title'] = self.title
        context['title_link'] = 'register'
        context['page_heading'] = self.title
        
        return context
    
    def form_valid(self, form):
        new_user = User()
        username = str(self.request.POST['firstName'] + '.' + self.request.POST['lastName'])
        new_user.username = username.lower()
        new_user.set_password(self.request.POST['password'])
        new_user.email = self.request.POST['email']
        new_user.first_name = self.request.POST['firstName']
        new_user.last_name = self.request.POST['lastName']
        new_user.save()
        g = Group.objects.get(name='user')
        g.user_set.add(new_user)
        new_user = authenticate(username=username, password=self.request.POST['password'])
        login(self.request, new_user)
        messages.success(self.request, "You have successfully created an account.")
        
        # send email to admin for notification of pending account
        subject = "A new user has registered!"
        message = """An account has been created and has to be approved:\n
\t%s\n
Click the link below to go to the pending users page.
http://www.tozerappraisals.com/users/pending
""" % username
        send_mail(subject, message, 'noreply@tozerappraisals.com', ['info@tozerappraisals.com'], fail_silently=False)
        
        return super(RegisterView, self).form_valid(form)
    
class ForgotPassView(FormView):
    template_name = 'account/forgot.html'
    title = 'Forgot Password'
    form_class = ForgotPassForm
    success_url = '/forgot'
    
    def get_context_data(self, form):
        context = super(ForgotPassView, self).get_context_data()
        context['forgot_form'] = form
        context['page_title'] = self.title
        context['title_link'] = 'forgot'
        context['page_heading'] = self.title
        
        return context
    
    def form_valid(self, form):
        insert_token = ForgotPass()
        # gets current date
        insert_token.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # adds two days to current date for setting token expiration
        insert_token.expirydate = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        # generate token
        signer = Signer()
        insert_token.token = signer.sign(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")).split(':')[3]
        # given email
        insert_token.email = self.request.POST['email']
        # get user based on email address given
        email = User.objects.filter(email=self.request.POST['email'])
        # if a user is found then send an email and save token to db
        if email:
            insert_token.save()
            # define email info
            subject = 'Password Reset Request for TozerAppraisals.com'
            message = """A request has been made to reset your account password. Please click the link below to continue.
http://www.tozerappraisals.com/reset/?token=%s\n
The link above is only available for a limited time and will expire 48 hours after the reset password form has been submitted.
If the link is expired by the time you click on it please submit a forgot password request again by using the link below.
http://www.tozerappraisals.com/forgot\n\n
If you're not sure why you have received this email then just ignore this message.
Please do not respond to this message.
""" % insert_token.token
            # send email
            send_mail(subject, message, 'noreply@tozerappraisals.com', [self.request.POST['email']], fail_silently=False)
        # return success message regardless of email existing in system or not
        messages.success(self.request, "An email has been sent! If you do not receive the email within 24 hours please use this form again.")
        return super(ForgotPassView, self).form_valid(form)
    
class ResetPassView(FormView):
    template_name = 'account/resetpass.html'
    title = 'Reset Password'
    form_class = ResetPassForm
    success_url = '/login'
    
    # the reason for using 'get' as opposed to 'get_context_data' is so we can use the redirect function
    # if we attempted to redirect with 'get_context_data' none of the context vars would be password and
    # the only thing that would be passed in the template
    # because we use 'get' we also have to use 'form_invalid'(along with 'form_valid') and return the form 
    # otherwise, once again, no variables will be passed and we will be met with a page that has no form
    # tl;dr you cannot use 'redirect' with 'get_context_data'
    def get(self, request):
        # if no token is set, redirect user back to home page
        if self.request.GET.get('token'):
            token = self.request.GET.get('token')
        else:
            return redirect(reverse('home'))
        
        # see if token exists in db and if not redirect user back to home page with error
        resetPass = ForgotPass.objects.get(token=token)
        if not resetPass:
            messages.error(self.request, "Invalid Token.")
            return redirect(reverse('home'))
        else:
            if resetPass.expirydate < datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"):
                messages.error(self.request, mark_safe("Token has expired. <a href='/forgot'>Click here</a> to reset your password."))
                return redirect(reverse('home'))

        context = super(ResetPassView, self).get_context_data()
        form = self.form_class
        context['reset_form'] = form
        context['page_title'] = self.title
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        # get email address
        token = self.request.GET.get('token')
        resetPass = ForgotPass.objects.get(token=token)
        # get user account based on email
        user = User.objects.get(email__exact=resetPass.email)
        # set new password and save data
        user.set_password(self.request.POST['password'])
        user.save()
        
        # set expiry date to now so user cannot use the same token twice
        resetPass.expirydate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resetPass.save()
        
        messages.success(self.request, "Your password has been updated! Please login below.")
        
        return super(ResetPassView, self).form_valid(form)
        
    def form_invalid(self, form):
        
        context = super(ResetPassView, self).get_context_data()
        context['reset_form'] = form
        context['page_title'] = self.title
        
        return self.render_to_response(context)

class AllUsersView(ListView):
    template_name = 'account/allusers.html'
    title = 'All Users'

    def get(self, request, page=1):
        if not self.request.user.has_perm('auth.view_all_users'):
            return redirect(reverse('orders:OrdersIndex'))
        
        # if certain keywords are found in sort then set self.sort_by to whatever sort method is chosen by user
        if request.GET.get('sort') in ['id', '-id', 'username', '-username', 'email', '-email']:
            self.sort_by = request.GET.get('sort')
        # if keywords are not found or sort is not set then go to default sorting method
        else:
            self.sort_by = 'id'
        
        # get all users
        users_list = User.objects.order_by(self.sort_by)
        
        # get number of pending user accounts
        pending_users = User.objects.filter(userprofile__approved=0)
        if pending_users:
            num_pending_users = len(pending_users)
        else:
            num_pending_users = 0
            
        #Paginator settings
        # 20 orders per page
        paginator = Paginator(users_list, 20)
        #Get the current page
        #page = request.GET.get('page')
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            #Deliver first page if page is not an integer
            users = paginator.page(1)
        except EmptyPage:
            #If page is out of range and doesn't exist, deliver last page
            users = paginator.page(paginator.num_pages)
        
        #Returning data            
        return render(
            request, 
            self.template_name,
            {
            'page_title': self.title,
            'title_link': 'users',
            'page_heading': self.title, 
            'all_users': users,
            'sort_by': self.sort_by,
            'num_pending_users': num_pending_users
            }
        )

class PendingUsersView(DetailView, FormView):
    template_name = 'account/pendingusers.html'
    title = 'Pending Users'
    
    def get(self, request, page=1):
        if not self.request.user.has_perm('auth.view_all_users'):
            return redirect(reverse('orders:OrdersIndex'))
        
        # if certain keywords are found in sort then set self.sort_by to whatever sort method is chosen by user
        if request.GET.get('sort') in ['id', '-id', 'username', '-username', 'email', '-email']:
            self.sort_by = request.GET.get('sort')
        # if keywords are not found or sort is not set then go to default sorting method
        else:
            self.sort_by = 'id'
        
        # if a user has been approved or denied, change value in db and send confirm message
        if request.GET.get('u') and request.GET.get('c'):
            username = request.GET.get('u')
            choice = request.GET.get('c')
            user = User.objects.get(username__exact=username)
            user_profile = user.get_profile()
            if choice == 'deny':
                user_profile.approved = 2
                user_profile.save()
                messages.warning(self.request, '%s has been banned and will no longer be able to access the site.' % username)
                return redirect(reverse('PendingUsers'))
            if choice == 'approve':
                user_profile.approved = 1
                user_profile.save()
                messages.success(self.request, '%s has been approved.' % username)
                return redirect(reverse('PendingUsers'))
        
        # get all users
        pending_users_list = User.objects.filter(userprofile__approved=0).order_by(self.sort_by)
        
        #Paginator settings
        # 20 orders per page
        paginator = Paginator(pending_users_list, 20)
        #Get the current page
        #page = request.GET.get('page')
        try:
            pending_users = paginator.page(page)
        except PageNotAnInteger:
            #Deliver first page if page is not an integer
            pending_users = paginator.page(1)
        except EmptyPage:
            #If page is out of range and doesn't exist, deliver last page
            pending_users = paginator.page(paginator.num_pages)
            
        #Returning data
        return render(
            request, 
            self.template_name,
            {
            'page_title': self.title,
            'title_link': 'users/pending',
            'page_heading': self.title, 
            'pending_users': pending_users,
            'sort_by': self.sort_by
            }
        )

class UserView(DetailView, FormView):
    template_name = 'account/user.html'
    model = User
    form_class = EditUserForm
    
    def get(self, request, *args, **kwargs):
        if not self.request.user.has_perm('auth.view_all_users'):
            return redirect(reverse('orders:OrdersIndex'))
        
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'User Not Found.')
            return redirect(reverse('ViewUser'))
        
        user_profile = self.object.get_profile()
        
        # below is for the approve/deny, ban, and unban buttons
        if request.GET.get('u'):
            # if user is pending and approve has been clicked
            if user_profile.approved == 0 and request.GET.get('u') == 'approve':
                user_profile.approved = 1
                user_profile.save()
                messages.success(request, 'User has been approved.')
            # if user is pending and deny has been clicked
            if user_profile.approved == 0 and request.GET.get('u') == 'deny':
                user_profile.approved = 2
                user_profile.save()
                messages.warning(request, 'User has been banned.')
            # if user is approved and ban is clicked
            if user_profile.approved == 1 and request.GET.get('u') == 'ban':
                user_profile.approved = 2
                user_profile.save()
                messages.warning(request, 'User has been banned.')
            # if user is banned and unban is clicked
            if user_profile.approved == 2 and request.GET.get('u') == 'unban':
                user_profile.approved = 1
                user_profile.save()
                messages.success(request, 'User has been unbanned.')
            
            # redirect back to user back
            return redirect('/user/' + str(self.object.id))
        
        if user_profile.locked == 1:
            messages.info(self.request, 'Account is locked. You cannot edit this account.')
            return redirect(reverse('AllUsers'))
        
        form = self.form_class
        context = super(UserView, self).get_context_data(object=self.object)
        context['page_title'] = 'User: ' + self.object.username
        context['page_heading'] = 'User: ' + self.object.username
        context['title_link'] = 'user/' + str(self.object.id)
        context['userid'] = self.object.id
        context['username'] = self.object.username
        context['approved'] = user_profile.approved
        context['edit_user_form'] = form({
            'username': self.object.username,
            'firstName': self.object.first_name,
            'lastName': self.object.last_name,
            'email': self.object.email,
            'accountType': self.object.groups.all()[0],
            'emailUpdates': user_profile.get_email,
            'hidden_username': self.object.username
        }, request=request)
        
        return self.render_to_response(context)
        
        return context
    
    def form_valid(self, form):
        self.object = self.get_object()
        user_profile = self.object.get_profile()
        self.success_url = '/user/' + str(self.object.id)
        
        self.object.username = self.request.POST['username']
        self.object.first_name = self.request.POST['firstName']
        self.object.last_name = self.request.POST['lastName']
        self.object.email = self.request.POST['email']
        
        # if user group has been changed
        if self.object.groups.all()[0] != self.request.POST['accountType']:
            old_group = self.object.groups.all()[0]
            new_group = self.request.POST['accountType']
            g = Group.objects.get(name=old_group)
            g.user_set.remove(self.object)
            g = Group.objects.get(name=new_group)
            g.user_set.add(self.object)
        
        # if users password has been changed
        if self.request.POST['new_password']:
            self.object.set_password(self.request.POST['new_password'])
        
        emailUpdates = 0
        if self.request.POST.get and 'emailUpdates' in self.request.POST and self.request.POST['emailUpdates'] == "on":
            emailUpdates = 1
        
        user_profile.get_email = emailUpdates
        
        user_profile.save()
        self.object.save()
        
        messages.success(self.request, '%s Updated!' % self.object.username)
        
        return super(UserView, self).form_valid(form)
    
    def form_invalid(self, form):
        self.object = self.get_object()
        context = super(UserView, self).get_context_data(object=self.object)
        context['page_title'] = 'User: ' + self.object.username
        context['page_heading'] = 'User: ' + self.object.username
        context['title_link'] = 'user/' + str(self.object.id)
        context['edit_user_form'] = form
        
        return self.render_to_response(context)

class CreateUserView(FormView):
    template_name = 'account/createuser.html'
    form_class = CreateUserForm
    
    def get(self, request):
        if not self.request.user.has_perm('auth.view_all_users'):
            return redirect(reverse('orders:OrdersIndex'))
        
        form = self.form_class
        context = super(CreateUserView, self).get_context_data()
        context['page_title'] = 'Create User'
        context['page_heading'] = 'Create User'
        context['title_link'] = 'user/create'
        context['create_user_form'] = form
        
        return self.render_to_response(context)
    
    def form_invalid(self, form):
        context = super(CreateUserView, self).get_context_data()
        context['page_title'] = 'Create User'
        context['page_heading'] = 'Create User'
        context['title_link'] = 'user/create'
        context['create_user_form'] = form
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        # create instance of a new user and define settings
        new_user = User()
        username = str(self.request.POST['firstName'] + '.' + self.request.POST['lastName'])
        new_user.username = username
        # generate a random password with a length of 8 consisting of uppercase letters and integers
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
        new_user.set_password(password)
        new_user.email = self.request.POST['email']
        new_user.first_name = self.request.POST['firstName']
        new_user.last_name = self.request.POST['lastName']
        # save new user in db
        new_user.save()
        # add user to group
        group = self.request.POST['accountType']
        g = Group.objects.get(name=group)
        g.user_set.add(new_user)
        # set user to have to change password on login and since user has been created by admin that means
        # the account is approved already
        user_profile = new_user.get_profile()
        user_profile.approved = 1
        user_profile.change_password = 1
        user_profile.save()
        
        # send email to new user
        subject = 'An account has been created for you at TozerAppraisals.com'
        message = """An account has been set up with the following details below:
Username: %s
Password: %s
\nYou will be required to change the password when you first login in order to fully access the site.
\nThis email has been sent automatically. Please do not respond to this message.
\n-Tozer Appraisal Services
""" % (username, password)

        send_mail(subject, message, 'noreply@tozerappraisals.com', [self.request.POST['email']], fail_silently=False)
        
        # set success url to new user account page
        newest_user = User.objects.latest('id')
        user_id = newest_user.id
        self.success_url = '/user/' + str(user_id)
        
        # success message
        messages.success(self.request, "The user has been successfully created.")
        
        return super(CreateUserView, self).form_valid(form)
            
            
class DeleteUserView(FormView, DetailView):
    model = User
    template_name = 'account/deleteuser.html'
    form_class = DeleteOrderForm
    
    def get(self, request, *args, **kwargs):
        if not self.request.user.has_perm('auth.view_all_users'):
            return redirect(reverse('orders:OrdersIndex'))
        
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'User Not Found.')
            return redirect(reverse('ViewUser'))
        
        user_profile = self.object.get_profile()
        if user_profile.locked == 1:
            messages.info(self.request, 'Account is locked. You cannot edit this account.')
            return redirect(reverse('AllUsers'))
        
        form = self.form_class
        context = super(DeleteUserView, self).get_context_data(object=self.object)
        context['page_title'] = 'Delete User: ' + str(self.object.username)
        context['page_heading'] = 'Delete User: ' + str(self.object.username)
        context['title_link'] = 'user/' + str(self.object.id) + '/delete'
        context['userid'] = self.object.id
        context['username'] = self.object.username
        context['delete_form'] = form
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        self.object = self.get_object()
        userID = str(self.object.username)
        
        if self.request.POST['deleteOrderConfirm'] in ['yes', 'Yes', 'y', 'Y']:
            # deleting order
            self.object.delete()
            messages.success(self.request, 'User ' + userID + ' deleted!')
            self.success_url = '/users'
        else: 
            messages.info(self.request, 'User ' + userID + ' not deleted!')
            self.success_url = '/user/' + str(self.object.id)
        
        return super(DeleteUserView, self).form_valid(form)
        
    def form_invalid(self, form):
        self.object = self.get_object()
        context = super(DeleteUserView, self).get_context_data(object=self.object)
        context['page_title'] = 'Delete User: ' + str(self.object.username)
        context['page_heading'] = 'Delete User: ' + str(self.object.username)
        context['title_link'] = 'user/' + str(self.object.id) + '/delete'
        context['userid'] = self.object.id
        context['username'] = self.object.username
        context['delete_form'] = form
        
        return self.render_to_response(context)