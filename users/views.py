from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            return render(request, 'users/register.html', {'form': form, 'registration_success': True})
        else:

            error_message = ""
            for _ , errors in form.errors.items():
                for error in errors:
                    error_message = error_message + error + '\\n'
            print("error")
            return render(request, 'users/register.html', {'form': form, 'registration_failure': True, 'error_message': error_message})
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return render(request, 'users/login.html', {'login_success': True})
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html', {'login_failure': True})
    return render(request, 'users/login.html')

@login_required  
def dashboard(request):
    return render(request, 'users/dashboard.html', {'user': request.user})

@login_required  # Ensure that only logged-in users can access this view
def logout_view(request):
    logout(request)  # This logs the user out
    messages.success(request, 'You have been logged out successfully.')
    return render(request, 'users/logout.html')