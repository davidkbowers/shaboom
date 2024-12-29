from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

def is_member(user):
    return user.user_type == 'member'

@login_required
@user_passes_test(is_member)
def member_dashboard(request):
    return render(request, 'accounts/member/dashboard.html')
