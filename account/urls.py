from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from account import views as account_view

urlpatterns = patterns('',
    url(r'^$', login_required(account_view.AccountView.as_view(), login_url='/login'), name='account_overview'),
)
