from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm, UserRegisterForm, FileRequestForm
from .models import File, FileRequest, UserProfile
import os
import subprocess
import psutil
import socket

# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip
def get_client_ip(request):
    wifi_ip = None
    for interface, addrs in psutil.net_if_addrs().items():
        # Iterate over addresses of each network interface
        for addr in addrs:
            if addr.family == socket.AF_INET:  # Use socket.AF_INET for IPv4 addresses
                # Check common interface names for Wi-Fi adapters across different OSes
                if 'wi-fi' in interface.lower() or 'wireless' in interface.lower() or 'wlan' in interface.lower() or 'en' in interface.lower():
                    wifi_ip = addr.address
                    break
        if wifi_ip:
            break

    return wifi_ip


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, status='not active')
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
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.status = 'active'
            user_profile.save()
            # messages.success(request, 'Login successful!')
            return render(request, 'users/login.html', {'login_success': True})
        else:
            # messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html', {'login_failure': True})
    return render(request, 'users/login.html')

@login_required  
def dashboard(request):
    return render(request, 'users/dashboard.html', {'user': request.user})

@login_required  # Ensure that only logged-in users can access this view
def logout_view(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.status = 'not active'
    user_profile.save()
    logout(request)  # This logs the user out
    # messages.success(request, 'You have been logged out successfully.')
    return render(request, 'users/logout.html')

@login_required
def upload_file(request):
    # Extract file request details
    request_id = request.GET.get('request_id')
    file_request = get_object_or_404(FileRequest, id=request_id)

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.uploader = request.user
            file_instance.description = file_request.file_name  
            file_instance.save()

            file_path = file_instance.file.path  
            try:
                receiver_ip = file_request.requester_ip
                subprocess.run(['python', 'fileTransfer/file_sender.py', file_path, receiver_ip], check=True)
                file_request.status = 'Completed'
                file_request.save()

                # Add success message
                messages.success(request, 'File uploaded and sent successfully!')
            except subprocess.CalledProcessError as e:
                # Handle any errors that occur when running the file_sender.py script
                messages.error(request, f"Error in file sending: {e}")

            return render(request, 'users/upload_file.html')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = FileUploadForm()

    return render(request, 'users/upload_file.html', {'form': form})


@login_required
def shared_files(request):
    query = request.GET.get('search', '')
    if query:
        files = File.objects.filter(description__icontains=query, uploader= request.user)  # Filter by description
        return render(request, 'users/shared_files.html', {'files': files})
    else:
        files = File.objects.filter(uploader=request.user)  # List all shared files
        return render(request, 'users/shared_files.html', {'files': files})

@login_required
def request_file(request):
    if request.method == 'POST':
        form = FileRequestForm(request.POST)
        if form.is_valid():
            file_request = form.save(commit=False)
            file_request.requester = request.user  # Set the requester to the logged-in user
            
            # Get the client's IP address and store it in the file request
            ip_address = get_client_ip(request)
            file_request.requester_ip = ip_address  
            print(file_request.requester_ip)
            file_request.save()
            try:
                subprocess.run(['python', 'fileTransfer\\file_receiver.py'], check=True)
                messages.success(request, 'File received successfully!')
            except subprocess.CalledProcessError as e:
                # Handle any errors that occur when running the file_sender.py script
                print(f"Error in file receiving: {e}")
                messages.error(request, f"Error in file receiving: {e}")
            return render(request, 'users/request_file.html')
    else:
        form = FileRequestForm()
    return render(request, 'users/request_file.html', {'form': form})

@login_required
def view_requests(request):
    file_requests = FileRequest.objects.filter(status = 'Pending').order_by('-requested_at')  # Get all file requests
    return render(request, 'users/view_requests.html', {'file_requests': file_requests})

@login_required
def active_users(request):
    online = UserProfile.objects.filter(status = 'active').exclude(user = request.user)
    offline = UserProfile.objects.filter(status = 'not active').exclude(user = request.user)
    return render(request, 'users/activeUsers.html', {'online':online, 'offline':offline})