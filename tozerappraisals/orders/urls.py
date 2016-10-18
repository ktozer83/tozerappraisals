from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from django.views.generic import RedirectView

from tozerappraisals.orders import views

urlpatterns = patterns('',
    # all orders
    url(r'^$', login_required(views.IndexView.as_view()), name='OrdersIndex'),
    # orders page
    url(r'^(?P<page>\d+)/$', login_required(views.IndexView.as_view())),
    # invalid input
    url(r'^(?P<page>\w+)/$', RedirectView.as_view(url='/orders/')),
    # redirected page
    url(r'^OrderNotFound/$', RedirectView.as_view(url='/orders/'), name='OrderNotFound')
)
