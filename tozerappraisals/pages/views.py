from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.generic.edit import FormView
from tozerappraisals.pages.forms import ContactForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError

from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
class IndexView(FormView):
    template_name = 'pages/index.html'
    title = 'Home'
    form_class = AuthenticationForm
    success_url = '/orders/'
    
    # in order to have the redirect we need to use the 'get' class.
    # as long as the user is not authenticated it will pass the form and whatever other variables
    # to the template.
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(reverse('orders:OrdersIndex'))
        else:
            form = self.form_class
            context = super(IndexView, self).get_context_data()
            context['login_form'] = form
            context['page_title'] = self.title
            
            return self.render_to_response(context)
            
    # as long as the form data is valid it will attempt to authenticate the user.
    # if it's not authenticated it will go back to the original page and an error message will be thrown.
    def form_valid(self, form):
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password'])
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
            self.success_url = '/orders/'
            return super(IndexView, self).form_valid(form)
    
    # if the form is not valid it will send the user back to the original page
    # using the original form as data along with whatever errors that were thrown.
    # we need to send the variables we used in the 'get' class above otherwise
    # they will not show up.
    def form_invalid(self, form):
        context = super(IndexView, self).get_context_data()
        context['login_form'] = form
        context['page_title'] = self.title
        
        return self.render_to_response(context)

class AboutView(View):
    template_name = 'pages/about.html'
    title = 'About Us'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title, 'page_heading': self.title, 'title_link': 'about'})
        
class ContactView(FormView):
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = '/contact'
    title = 'Contact'
    
    def get_context_data(self, form):
        return {'page_title': self.title, 'page_heading': self.title, 'title_link': 'contact', 'form': form}
    
    def form_valid(self, form):
        # define email info and send email
        subject = "You have a new message!"
        message = """This message has been submitted via the contact form from Tozer Appraisal Services.\n
\tSubmitted by: %s\n
\tReturn Email: %s\n
\tComment/Question:
\t%s\n
This message was sent by the server. Do not reply to this message.""" % (self.request.POST['name'], self.request.POST['email'], self.request.POST['message'])
        # sending email
        try:
            send_mail(subject, message, 'noreply@tozerappraisals.com', ['info@tozerappraisals.com'], fail_silently=False)
            messages.success(self.request, "Your message has been sent! We will get back to you as soon as possible!")
        except BadHeaderError:
            messages.error(self.request, "Unable to send message. Please try again.")
        return super(ContactView, self).form_valid(form)
        
class ContactSentView(View):
    template_name = 'pages/contact_sent.html'
    title = 'Contact'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title, 'title_link': 'contact', 'page_heading': self.title})

class ServicesView(View):
    template_name = 'pages/services.html'
    title = 'Services'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title, 'page_heading': self.title, 'title_link': 'services'})

class ServicesCoverageView(View):
    template_name = 'pages/services_coverage.html'
    title = 'Coverage Area'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title, 'page_heading': self.title, 'title_link': 'services/coverage'})
    
class ServicesFactsView(View):
    template_name = 'pages/services_facts.html'
    title = 'Appraisal Facts'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title, 'page_heading': self.title, 'title_link': 'services/facts'})

class FaqView(View):
    template_name = 'pages/faq.html'
    title = 'Frequently Asked Questions'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title, 'page_heading': self.title, 'title_link': 'faq'})
    
class Custom404View(View):
    template_name = 'pages/404.html'
    title = 'Page Not Found'
    
    def get(self, request):
        return render(request, self.template_name, {'page_title': self.title})