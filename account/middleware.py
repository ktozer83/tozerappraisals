from django.shortcuts import redirect
from django.contrib import messages

# the below middleware will get if a user needs to change their password as long as they are logged in
# this checks no matter what page they are on so that way if a user does need to change their password
# they won't have access to the site until they have changed it
class CheckForChangePassword(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            user_profile = request.user.get_profile()
            if user_profile.change_password == 1 and request.path not in '/account/':
                messages.info(request, 'Please update your password before continuing.')
                return redirect('/account')