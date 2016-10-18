from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView
# import pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
# import messages
from django.contrib import messages
# import FormView
from django.views.generic.edit import FormView, FormMixin
# import edit order form
from tozerappraisals.orders.forms import DeleteOrderForm, OrderForm, EditMessageForm, GotoOrderForm, UploadReportForm
from django.core.mail import send_mail, BadHeaderError
#import random string generator
from django.utils.crypto import get_random_string

from django.conf import settings

from django.core.urlresolvers import reverse

#import anything order related
from tozerappraisals.orders.models import Order, Update, Comment, WelcomeMessage, UploadReport

# import datetime
from datetime import datetime

# import re to allow regular expressions
import re

from django.contrib.auth.models import User

# Create your views here.
class IndexView(ListView, FormMixin):
    template_name = 'orders/orders.html'
    title = 'Home'
    form_class = GotoOrderForm
    # Get welcome message
    welcome_message = WelcomeMessage.objects.get(id=1)
    
    def get(self, request, page=1):
        
        # this is for normal users, if this is not set an error will be thrown
        num_pending_users = False
        
        # if certain keywords are found in sort then set self.sort_by to whatever sort method is chosen by user
        if request.GET.get('sort') in ['orderID', '-orderID', 'address', '-address', 'applicantName', '-applicantName', 'status', '-status']:
            self.sort_by = request.GET.get('sort')
        # if keywords are not found or sort is not set then go to default sorting method
        else:
            self.sort_by = '-orderID'
            
        #Custom permission is set in models.py
        if self.request.user.has_perm('orders.view_all_orders'):
            # get all orders for admin to see
            orders_list = Order.objects.order_by(self.sort_by)
            
            # get number of pending user accounts
            pending_users = User.objects.filter(userprofile__approved=0)
            if pending_users:
                num_pending_users = len(pending_users)
            else:
                num_pending_users = 0
            
            # if the order has been viewed or not set this for the admin to see
            viewed_row = {0: 'New!', 1: ''}
            updated_row = {0: '', 1: ''}
        else:
            # get orders for the user that is logged in since they are not an admin
            orders_list = Order.objects.filter(username=self.request.user.username).order_by(self.sort_by)
            
            # if order has been viewed or not by admin doesn't matter for regular user, but unless this is set an error
            # will be thrown
            viewed_row = {0: '', 1: ''}
            # updated only applies to user and not admin so set notification
            updated_row = {0: '', 1: 'Updated!'}
        
        #Paginator settings
        # 20 orders per page
        paginator = Paginator(orders_list, 20)
        #Get the current page
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            #Deliver first page if page is not an integer
            orders = paginator.page(1)
        except EmptyPage:
            #If page is out of range and doesn't exist, deliver last page
            orders = paginator.page(paginator.num_pages)
        
        form = self.form_class
        
        #Returning data
        return render(
            request, 
            self.template_name,
            {
            'page_title': self.title,
            'title_link': 'orders',
            'page_heading': self.title, 
            'all_orders': orders,
            'updated_row': updated_row,
            'viewed_row': viewed_row,
            'sort_by': self.sort_by,
            'num_pending_users': num_pending_users,
            'welcome_message': self.welcome_message.message,
            'goto_order_form': form
            }
        )
    
    def get_success_url(self):
        return '/order/' + self.request.POST['goto_order']
    
    def post(self, request, page=1, *args, **kwargs):
        form = self.form_class(self.request.POST)
        
        if form.is_valid():
            return super(IndexView, self).form_valid(form)
        
        else:
            # this is all redundant but I could not find a way to have everything in 'def get()' be shown again
            # and have the errors show, so this will have to do until then
            
            # this is for normal users, if this is not set an error will be thrown
            num_pending_users = False
            
            # if certain keywords are found in sort then set self.sort_by to whatever sort method is chosen by user
            if request.GET.get('sort') in ['orderID', '-orderID', 'address', '-address', 'applicantName', '-applicantName', 'status', '-status']:
                self.sort_by = request.GET.get('sort')
            # if keywords are not found or sort is not set then go to default sorting method
            else:
                self.sort_by = '-orderID'
                
            #Custom permission is set in models.py
            if self.request.user.has_perm('orders.view_all_orders'):
                # get all orders for admin to see
                orders_list = Order.objects.order_by(self.sort_by)
                
                # get number of pending user accounts
                pending_users = User.objects.filter(userprofile__approved=0)
                if pending_users:
                    num_pending_users = len(pending_users)
                else:
                    num_pending_users = 0
                
                # if the order has been viewed or not set this for the admin to see
                viewed_row = {0: 'New!', 1: ''}
                updated_row = {0: '', 1: ''}
            else:
                # get orders for the user that is logged in since they are not an admin
                orders_list = Order.objects.filter(username=self.request.user.username).order_by(self.sort_by)
                
                # if order has been viewed or not by admin doesn't matter for regular user, but unless this is set an error
                # will be thrown
                viewed_row = {0: '', 1: ''}
                # updated only applies to user and not admin so set notification
                updated_row = {0: '', 1: 'Updated!'}
            
            #Paginator settings
            # 20 orders per page
            paginator = Paginator(orders_list, 20)
            #Get the current page
            try:
                orders = paginator.page(page)
            except PageNotAnInteger:
                #Deliver first page if page is not an integer
                orders = paginator.page(1)
            except EmptyPage:
                #If page is out of range and doesn't exist, deliver last page
                orders = paginator.page(paginator.num_pages)
            
            #Returning data
            return render(
                request, 
                self.template_name,
                {
                'page_title': self.title,
                'title_link': 'orders',
                'page_heading': self.title, 
                'all_orders': orders,
                'updated_row': updated_row,
                'viewed_row': viewed_row,
                'sort_by': self.sort_by,
                'num_pending_users': num_pending_users,
                'welcome_message': self.welcome_message.message,
                'goto_order_form': form
                }
            )
        
class ViewOrder(DetailView):
    model = Order
    template_name = 'orders/vieworder.html'
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        
        # If user is not one who created order, and is not admin, redirect
        # convert both usernames to lower to make sure everything matches
        if self.request.user.username.lower() != self.object.username.lower() and not self.request.user.has_perm('orders.view_any_order'):
            # redirect back to '/orders/' with order not found message
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        else:
            # Order data, also comments and upgrades linked to order
            context = self.get_context_data(object=self.object)
            context['orderComments'] = Comment.objects.filter(orderNumber=self.object.orderID).order_by('-commentDate')
            context['orderUpdates'] = Update.objects.filter(orderNumber_id=self.object.orderID).order_by('-updateDate')
            # other page data
            context['page_title'] = 'Order: ' + self.object.address
            context['title_link'] = 'order/' + str(self.object.orderID)
            context['page_heading'] = self.object.address
            
            # If the order is new and is being viewed for the first time
            # update viewed column
            if self.object.viewed == 0 and self.request.user.has_perm('orders.view_any_order'):
                self.object.viewed = 1
                self.object.save()
            
            # if a regular user views the article and it's been updated, this sets updated to not updated
            if self.object.updated == 1 and not self.request.user.has_perm('orders.view_any_order'):
                self.object.updated = 0
                self.object.save()
            
            context['contacted_row'] = {
                0: 'Client Not Contacted',
                1: 'Client Contacted'
            }
            
        return self.render_to_response(context)
    
class MapOrderView(DetailView):
    template_name = 'orders/map.html'
    model = Order
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        
        # If user is not one who created order, and is not admin, redirect
        if self.request.user.username.lower() != self.object.username.lower() and not self.request.user.has_perm('orders.view_any_order'):
            # redirect back to '/orders/' with order not found message
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        else:
            # create map url
            address = self.object.address.split(" ")
            address = ("+").join(address)
            city = self.object.city
            if ' ' in city and not ',' in city:
                city = city.split(" ")
                city = city[0]
            elif ',' in city:
                city = city.split(",")
                strip_city = re.compile(r'[^a-zA-Z]+')
                city = strip_city.sub('', city[0])
    
            url = "https://maps.googleapis.com/maps/api/staticmap?center=" + address + ",+" + city + ",+Ontario" + "&size=600x400&zoom=12&sensor=true&markers=color:blue|" + address + ",+" + city + ",+Ontario"

            
            # Order data, also comments and upgrades linked to order
            context = self.get_context_data(object=self.object)
            context['page_title'] = 'View Map: ' + self.object.address
            context['page_heading'] = 'View Map: ' + self.object.address
            context['title_link'] = 'order/' + str(self.object.orderID) + '/map'
            context['map_url'] = url
            
        return self.render_to_response(context)
    
class PrintOrderView(DetailView):
    template_name = 'orders/printorder.html'
    model = Order
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        
        # If user is not one who created order, and is not admin, redirect
        if self.request.user.username.lower() != self.object.username.lower() and not self.request.user.has_perm('orders.view_any_order'):
            # redirect back to '/orders/' with order not found message
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        else:
            # Order data, also comments and upgrades linked to order
            context = self.get_context_data(object=self.object)
            context['page_title'] = 'Order: ' + self.object.address
            context['page_heading'] = self.object.address
            
            context['contacted_row'] = {
                0: 'Client Not Contacted',
                1: 'Client Contacted'
            }
            
        return self.render_to_response(context)

class EditOrderView(DetailView, FormView):
    model = Order
    template_name = 'orders/editorder.html'
    form_class = OrderForm
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        
        # If user is not one who created order, and is not admin, redirect
        if self.request.user.username.lower() != self.object.username.lower() and not self.request.user.has_perm('orders.view_any_order'):
            # redirect back to '/orders/' with order not found message
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        
        # split inspectionDate
        if self.object.inspectionDate:
            inspection_split = self.object.inspectionDate.split(' ')
            inspection_date = str(inspection_split[0])
            inspection_hour, inspection_minute =  inspection_split[1].split(':')
            if inspection_split[2] in 'a.m.':
                inspection_period_am = True
                inspection_period_pm = False
            elif inspection_split[2] in 'p.m.':
                inspection_period_am = False
                inspection_period_pm = True
        else:
            inspection_date = ''
            inspection_hour = '10'
            inspection_minute = '30'
            inspection_period_am = True
            inspection_period_pm = False
            
        
        form = self.form_class
        context = super(EditOrderView, self).get_context_data(object=self.object)
        context['page_title'] = 'Edit Order: ' + self.object.address
        context['page_heading'] = 'Edit Order: ' + self.object.address
        context['title_link'] = 'order/' + str(self.object.orderID) + '/edit'
        context['edit_form'] = form({
            'applicantName': self.object.applicantName,
            'contactNum': self.object.contactNum,
            'address': self.object.address,
            'city': self.object.city,
            'dueDate': self.object.dueDate,
            'appType': self.object.appType
        })
        context['inspectionDate'] = inspection_date,
        context['inspectionHour'] = str(inspection_hour),
        context['inspectionMinute'] = inspection_minute,
        context['inspectionPeriod_am'] = inspection_period_am,
        context['inspectionPeriod_pm'] = inspection_period_pm
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        self.updates = ''
        self.object = self.get_object()
        self.success_url = '/order/' + str(self.object.orderID)
        # only appraiser can affect inspection date
        if self.request.user.has_perm('orders.view_any_order'):
            if self.request.POST['inspectionDate']:
                inspectionDate = self.request.POST['inspectionDate'] + ' ' + self.request.POST['inspectionHour'] + ':' + self.request.POST['inspectionMinute'] + ' ' + self.request.POST['inspectionPeriod']
            else:
                inspectionDate = ''
        # this is to save info into order updates db.
        # there are two dictionaries, as a user does not have the same options an appraiser does
        compare_values_user = {
            self.object.applicantName: [self.request.POST['applicantName'], 'Applicant Name'],
            self.object.contactNum: [self.request.POST['contactNum'], 'Contact Number'],
            self.object.address: [self.request.POST['address'], 'Address'],
            self.object.city: [self.request.POST['city'], 'City'],
            self.object.dueDate: [self.request.POST['dueDate'], 'Due Date'],
            self.object.appType: [self.request.POST['appType'], 'Appraisal Type'] 
        }
        
        # if the old data is different than the post data we know that it was changed, so
        # insert the updated field into the updates database
        def compare_values(values_dict):
            for key in values_dict:
                if str(key) != str(values_dict[key][0]):
                    update = Update()
                    update.orderNumber_id = self.object.orderID
                    update.update = str(values_dict[key][1])
                    update.username = self.request.user.username.lower()
                    update.updateDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update.save()
                    
                    self.updates = self.updates + str(values_dict[key][1]) + '\n'
                    
                    # if order was updated by admin then set updated value to true
                    if self.request.user.has_perms('orders.view_any_order'):
                        self.object.updated = 1
                        self.object.save()
        
        # compare values for user
        compare_values(compare_values_user)
        
        # remove characters from contactNum
        contactNum = self.request.POST['contactNum']
        strip_contactNum = re.compile(r'[^\d]+')
        contactNum = strip_contactNum.sub('', contactNum)
        
        # saving order data into db. Whatever was changed will be reflected in the post data
        # and it will be saved into order db.
        self.object.applicantName = self.request.POST['applicantName']
        self.object.contactNum = contactNum
        self.object.address = self.request.POST['address']
        self.object.city = self.request.POST['city']
        self.object.dueDate = self.request.POST['dueDate']
        self.object.appType = self.request.POST['appType']
        if self.request.user.has_perm('orders.view_any_order'):
            #compare values for appraiser
            compare_values_appraiser = {
                self.object.status: [self.request.POST['status'], 'Status'],
                str(self.object.contacted): [str(self.request.POST['contacted']), 'Contacted'],
                self.object.inspectionDate: [inspectionDate, 'Inspection Date']
            }
            compare_values(compare_values_appraiser)
            
            self.object.contacted = self.request.POST['contacted']
            self.object.status = self.request.POST['status']
            self.object.inspectionDate = inspectionDate
        self.object.save()
        
        # if a comment has been added it needs to be inserted into another table
        if self.request.POST['comments']:
            comment = Comment()
            # In order for comment.orderNumber to be an instance of the order the comment is being assigned to
            # we must make an instance of the order we are on.
            # what the code below does is create an instance of an order with the ID that we are using above.
            # We can't simply set it to be a number as a number is not an instance of an object.
            comment.orderNumber = Order.objects.get(orderID=self.object.orderID)
            comment.comment = self.request.POST['comments']
            comment.username = self.request.user.username.lower()
            comment.commentDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # insert update into db stating a comment was placed as well
            update = Update()
            update.orderNumber_id = self.object.orderID
            update.update = 'Comment'
            update.username = self.request.user.username.lower()
            update.updateDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.updates = self.updates + 'Comments Added' + '\n'
            
            # Save to database
            update.save()            
            comment.save()
            
        # send an email regarding updates as long as there are updates
        if self.updates != '':
            subject = 'Updates have been made to order ' + str(self.object.orderID)
            message = """The following updates have been made:
%s
To view the order click the link below:
http://www.tozerappraisals.com/order/%s\n
-Tozer Appraisal Services\n
This email has been sent automatically. Please do not reply to it.""" % (self.updates, self.object.orderID)
            # if an appraiser updated order send email to user as long as they choose to receive updates
            # since only appraisers and the user who submitted the order can edit said order then it makes sense
            # that if the username that's logged in doesn't match the username associated with the order an appraiser
            # did the edit
            # get the email linked to the username on the order
            user = User.objects.get(username=self.object.username)
            # get the users profile
            user_profile = user.get_profile()
            if self.request.user.username.lower() != self.object.username.lower() and user_profile.get_email == 1:
                send_mail(subject, message, 'noreply@tozerappraisals.com', [user.email], fail_silently=False)
            # if user updated the order then send email to admin
            if self.request.user.username.lower() == self.object.username.lower():
                send_mail(subject, message, 'noreply@tozerappraisals.com', ['info@tozerappraisals.com'], fail_silently=False)            

        messages.success(self.request, 'Order Updated!')
        
        return super(EditOrderView, self).form_valid(form)
    
    def form_invalid(self, form):
        self.object = self.get_object()
        
        if self.request.POST['inspectionPeriod'] in 'a.m.':
            inspectionPeriod_am = True
            inspectionPeriod_pm = False
        else:
            inspectionPeriod_am = True
            inspectionPeriod_pm = False
        
        context = super(EditOrderView, self).get_context_data(object=self.object)
        context['page_title'] = 'Edit Order: ' + self.object.address
        context['page_heading'] = 'Edit Order: ' + self.object.address
        context['title_link'] = 'order/' + str(self.object.orderID) + '/edit'
        context['edit_form'] = form
        context['inspectionDate'] = self.request.POST['inspectionDate'],
        context['inspectionHour'] = self.request.POST['inspectionHour'],
        context['inspectionMinute'] = self.request.POST['inspectionMinute'],
        context['inspectionPeriod_am'] = inspectionPeriod_am,
        context['inspectionPeriod_pm'] = inspectionPeriod_pm
        
        return self.render_to_response(context)
    
class DeleteOrderView(FormView, DetailView):
    model = Order
    template_name = 'orders/deleteorder.html'
    form_class = DeleteOrderForm
    
    def get(self, request, *args, **kwargs):
        
        if not self.request.user.has_perm('orders.view_all_orders'):
            return redirect(reverse('orders:OrdersIndex'))
        
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'Order Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        form = self.form_class
        context = super(DeleteOrderView, self).get_context_data(object=self.object)
        context['page_title'] = 'Delete Order: ' + str(self.object.orderID)
        context['page_heading'] = 'Delete Order: ' + str(self.object.orderID)
        context['title_link'] = 'order/' + str(self.object.orderID) + '/delete'
        context['delete_form'] = form
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        self.object = self.get_object()
        orderID = str(self.object.orderID)
        
        if self.request.POST['deleteOrderConfirm'] in ['yes', 'Yes', 'y', 'Y']:
            # deleting order
            self.object.delete()
            messages.success(self.request, 'Order ' + orderID + ' deleted!')
            self.success_url = '/orders'
        else: 
            messages.info(self.request, 'Order ' + orderID + ' not deleted!')
            self.success_url = '/order/' + str(self.object.orderID)
        
        return super(DeleteOrderView, self).form_valid(form)
        
    def form_invalid(self, form):
        self.object = self.get_object()
        context = super(DeleteOrderView, self).get_context_data(object=self.object)
        context['page_title'] = 'Delete Order: ' + str(self.object.orderID)
        context['page_heading'] = 'Delete Order: ' + str(self.object.orderID)
        context['title_link'] = 'order/' + str(self.object.orderID) + '/delete'
        context['delete_form'] = form
        
        return self.render_to_response(context)
    
class NewOrderView(FormView):
    template_name = 'orders/neworder.html'
    title = 'New Order'
    form_class = OrderForm
    
    def get(self, request, *args, **kwargs):
        # if user has not been approved and has already submitted an order then redirect to orders page
        # get user info
        user = User.objects.filter(username=self.request.user.username)
        user_profile = request.user.get_profile()
        # get number of orders the user has submitted
        num_orders = Order.objects.filter(username=self.request.user.username).count()
        if user_profile.approved == 0 and num_orders >= 1:
            messages.error(request, "You can't submit another order until your account has been approved by the administration.")
            return redirect(reverse('orders:OrdersIndex'))
        
        form = self.form_class
        context = super(NewOrderView, self).get_context_data()
        context['new_order_form'] = form
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'order/new'
            
        return self.render_to_response(context)
        
    def form_valid(self, form):
        self.success_url = '/orders/'
        order = Order()
        
        # remove characters from contactNum
        contactNum = self.request.POST['contactNum']
        strip_contactNum = re.compile(r'[^\d]+')
        contactNum = strip_contactNum.sub('', contactNum)
        
        order.applicantName = self.request.POST['applicantName']
        order.contactNum = contactNum
        order.address = self.request.POST['address']
        order.city = self.request.POST['city']
        order.dueDate = self.request.POST['dueDate']
        order.appType = self.request.POST['appType']
        order.comments = self.request.POST['comments']
        order.orderDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order.username = self.request.user.username.lower()
        order.save()
        
        # send email to admin for notification of new order
        # get id of order that's just been submitted
        latest_order = Order.objects.latest('orderID')
        orderID = latest_order.orderID
        subject = 'An order has been submitted!'
        message = """A new order has been placed on TozerAppraisals.com\n
\t%s
\t%s\n
Click the link below to go to the order.
http://www.tozerappraisals.com/order/%s""" % (self.request.POST['applicantName'], self.request.POST['address'], orderID)
        
        send_mail(subject, message, 'noreply@tozerappraisals.com', ['info@tozerappraisals.com'], fail_silently=False)
        
        messages.success(self.request, 'Your order has been submitted!')
        
        return super(NewOrderView, self).form_valid(form)
    
    def form_invalid(self, form):
        context = super(NewOrderView, self).get_context_data()
        context['new_order_form'] = form
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'order/new'
        
        return self.render_to_response(context)
    
# this doesn't have anything really to do with orders other than the fact that the welcome message
# is viewed on the orders page. I just didn't want to have to create another map for something as simple
# as a welcome message
class EditMessageView(FormView):
    model = WelcomeMessage
    template_name = 'orders/editwelcome.html'
    success_url = '/orders'
    form_class = EditMessageForm
    title = 'Edit Welcome Message'
    
    def get(self, request):
        self.object = WelcomeMessage.objects.get(id=1)
        # make sure user is allowed to view this page
        if not self.request.user.has_perm('welcomemessage.edit_welcome_message'):
            return redirect(reverse('orders:OrdersIndex'))
        
        form = self.form_class
        context = super(EditMessageView, self).get_context_data(object=self.object)
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'editwelcome'
        context['last_updated'] = self.object.last_updated
        context['username'] = self.object.username.lower()
        context['edit_message_form'] = form({
            'message': self.object.message
        })
        
        return self.render_to_response(context)
    
    def form_valid(self, form):
        self.success_url = '/orders/'
        
        self.object = WelcomeMessage.objects.get(id=1)
        
        self.object.message = self.request.POST['message']
        self.object.username = self.request.user.username.lower()
        
        self.object.save()
        
        messages.success(self.request, 'The welcome message has been updated!')
        
        return super(EditMessageView, self).form_valid(form)
        
    def form_invalid(self, form):
        
        self.object = WelcomeMessage.objects.get(id=1)
        
        context = super(EditMessageView, self).get_context_data()
        context['edit_message_form'] = form
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'editwelcome'
        context['last_updated'] = self.object.last_updated
        context['username'] = self.object.username.lower()
        
        return self.render_to_response(context)
    
class UploadReportView(FormView):
    template_name = 'orders/uploadReport.html'
    title = 'Upload Report'
    form_class = UploadReportForm
    model = UploadReport
    
    def get(self, request):
        
        if not self.request.user.has_perm('orders.view_all_orders'):
            return redirect(reverse('orders:OrdersIndex'))
        
        self.sort_by = "-id"
        
        uploaded_reports = UploadReport.objects.order_by(self.sort_by)
        
        form = self.form_class
        context = super(UploadReportView, self).get_context_data()
        context['upload_report_form'] = form
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'uploadReport'
        context['uploaded_reports'] = uploaded_reports
            
        return self.render_to_response(context)

    def form_valid(self, form):
        self.success_url = '/uploadReport/'
        report = UploadReport()
        
        file = self.request.FILES['file']
        
        report.filename = get_random_string(length=64) + '.pdf'
        report.file = file.name
        report.username = self.request.user.username.lower()
        report.uploadDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report.save()
        
        with open(settings.PROJECT_ROOT + '/pages/static/pages/reports/' + file.name , 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        messages.success(self.request, 'Report has been uploaded!')
        
        return super(UploadReportView, self).form_valid(form)
    
    def form_invalid(self, form):
        context = super(UploadReportView, self).get_context_data()
        context['upload_report_form'] = form
        context['page_title'] = self.title
        context['page_heading'] = self.title
        context['title_link'] = 'uploadReport'
        
        return self.render_to_response(context)
    
class GetReport(DetailView):
    model = UploadReport
    template_name = 'orders/getReport.html'
    
    def get_object(self):
        return UploadReport.objects.get(filename=self.kwargs.get("filename"))
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'Report Not Found.')
            return redirect(reverse('orders:OrdersIndex'))
        
        context = self.get_context_data(object=self.object)
        context['page_title'] = 'Report: ' + self.object.file
        context['title_link'] = 'report/' + str(self.object.filename)
        context['page_heading'] = 'Report: ' + self.object.file
        context['report'] = self.object
        
        return self.render_to_response(context)