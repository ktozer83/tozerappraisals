from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from tozerappraisals.pages import views as pages_view
from account import views as account_view
from tozerappraisals.orders import views as order_views
from django.views.generic import RedirectView

handler404 = 'pages.views.Custom404View'

urlpatterns = patterns('',
    # home
    url(r'^$', pages_view.IndexView.as_view(), name='home'),
    # about
    url(r'^about/$', pages_view.AboutView.as_view(), name='about'),
    # services
    url(r'^services/$', pages_view.ServicesView.as_view(), name='Services'),
    url(r'^services/coverage/$', pages_view.ServicesCoverageView.as_view(), name='ServicesCoverage'),
    url(r'^services/facts/$', pages_view.ServicesFactsView.as_view(), name='ServicesFacts'),
    # faq
    url(r'^faq/$', pages_view.FaqView.as_view(), name='faq'),
    # account related
    url(r'^account/', include('account.urls', namespace='account')),
    # contact
    url(r'^contact/$', pages_view.ContactView.as_view(), name='contact'),
    url(r'^contact/sent/$', pages_view.ContactSentView.as_view()),
    # login
    url(r'^login/$', account_view.LoginView.as_view(), name='login'),
    # logout
    url(r'^logout/$', account_view.LogoutView.as_view(), name='logout'),
    # register
    url(r'^register/$', account_view.RegisterView.as_view(), name='register'),
    # forgot password
    url(r'^forgot/$', account_view.ForgotPassView.as_view(), name='forgotPass'),
    # reset password
    url(r'^reset/$', account_view.ResetPassView.as_view(), name='resetPass'),
    # orders
    url(r'^orders/', include('tozerappraisals.orders.urls', namespace='orders')),
    # specific order
    url(r'^order/new/$', login_required(order_views.NewOrderView.as_view()), name='NewOrder'),
    url(r'^order/(?P<pk>\d+)/$', login_required(order_views.ViewOrder.as_view()), name='ViewOrder'),
    url(r'^order/(?P<pk>\d+)/edit/$', login_required(order_views.EditOrderView.as_view()), name='EditOrder'),
    url(r'^order/(?P<pk>\d+)/print/$', login_required(order_views.PrintOrderView.as_view()), name='PrintOrder'),
    url(r'^order/(?P<pk>\d+)/delete/$', login_required(order_views.DeleteOrderView.as_view()), name='DeleteOrder'),
    url(r'^order/(?P<pk>\d+)/map/$', login_required(order_views.MapOrderView.as_view()), name='MapOrder'),
    url(r'^order/(?P<pk>\w+)/$', RedirectView.as_view(url='/orders/')),
    # all users related(admin only)
    url(r'^users/(?P<page>\d+)/$', login_required(account_view.AllUsersView.as_view())),
    url(r'^users/pending/(?P<page>\d+)/$', login_required(account_view.PendingUsersView.as_view())),
    url(r'^users/pending/$', login_required(account_view.PendingUsersView.as_view()), name='PendingUsers'),
    url(r'^user/create/$', login_required(account_view.CreateUserView.as_view()), name='CreateUser'),
    url(r'^user/(?P<pk>\d+)/delete/$', login_required(account_view.DeleteUserView.as_view()), name='DeleteUser'),
    url(r'^user/(?P<pk>\d+)/$', login_required(account_view.UserView.as_view()), name='ViewUser'),
    url(r'^users/$', login_required(account_view.AllUsersView.as_view()), name='AllUsers'),
    # edit welcome message
    url(r'^editwelcome/$', login_required(order_views.EditMessageView.as_view()), name='EditMessage'),
    # upload report(admin only)
    url(r'^uploadReport/', login_required(order_views.UploadReportView.as_view()), name='AllUsers'),
    url(r'^report/(?P<filename>.*?)/$', order_views.GetReport.as_view()),
)
