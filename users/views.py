from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from users.forms import CustomUserCreationForm

# Dashboard of the site's users
def dashboard_user(req):
    all_users = User.objects.all()
    return render(request = req, template_name = 'users/dashboard.html', context = {'all_users': all_users})

def register_user(request):
    if(request.method == "POST"):
        my_custom_form = CustomUserCreationForm(request.POST)
        if(my_custom_form.is_valid):
            my_user = my_custom_form.save()
            login(request = request, user = my_user)
            return HttpResponseRedirect(reverse(viewname = 'index'))
    else:
        return render(
            request = request, 
            template_name = 'users/register_user.html', 
            context = {'my_custom_form': CustomUserCreationForm})
