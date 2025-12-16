from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def security_check(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.POST.get('user')
        
        # Check both user and password
        if user == settings.SECURITY_USER and password == settings.SECURITY_PASSWORD:
            request.session['authenticated'] = True
            # Redirect to welcome page or the page they were trying to access
            next_url = request.GET.get('next', '/welcome')
            return redirect(next_url)
        else:
            messages.error(request, 'Utilisateur ou mot de passe incorrect')
    
    return render(request, 'security/login.html')