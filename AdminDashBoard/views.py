from django.shortcuts import render, redirect

def login(request):
    if request.method == 'POST':
        admin_name = request.POST.get('admin_name')
        password = request.POST.get('password')
        # Here, you would implement your verification logic
        # For simplicity, I'll just check if admin_name and password are not empty
        if admin_name and password:
            # Redirect to admin dashboard if login successful
            return redirect('admin_dashboard')
    return render(request, 'login.html')

def admin_dashboard(request):
    # Add logic for admin dashboard here
    return render(request, 'admin_dashboard.html')