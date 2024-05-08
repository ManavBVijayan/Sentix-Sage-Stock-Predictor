from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import ProcessLog


def login(request):
    if request.method == 'POST':
        admin_name = request.POST.get('admin_name')
        password = request.POST.get('password')
        user = authenticate(request, username=admin_name, password=password)
        if user is not None and user.is_superuser:
            auth_login(request, user)  # Changed the function name here
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or user is not a superuser.')
    return render(request, 'login.html')


def admin_dashboard(request):
    processlogs = ProcessLog.objects.all()
    paginator = Paginator(processlogs, 10)  # Show 15 entries per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard.html', {'page_obj': page_obj})


def logout_view(request):
    request.session.clear()
    logout(request)
    return redirect('home')
