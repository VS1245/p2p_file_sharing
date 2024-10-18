from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm, UserRegisterForm, FileRequestForm
from .models import File, FileRequest
import os
import subprocess
from django.conf import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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

# @login_required
# def upload_file(request):
#     if request.method == 'POST':
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             file_instance = form.save(commit=False)
#             file_instance.uploader = request.user
#             file_instance.save()
#             messages.success(request, 'File uploaded successfully!')
#             return redirect('shared_files')
#     else:
#         form = FileUploadForm()
#     return render(request, 'users/upload_file.html', {'form': form})

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded file
            file_instance = form.save(commit=False)
            file_instance.uploader = request.user
            file_instance.save()

            # Get the requester's IP address
            ip_address = request.META.get('REMOTE_ADDR')

            # Save the file request information
            file_request = FileRequest.objects.create(
                file_name=file_instance.file.name,  # Save the file name
                requester=request.user,  # The user requesting the file
                ip_address=ip_address  # The requester's IP
            )
            file_request.save()

            # Call the `file_sender.py` script with the file path
            file_path = file_instance.file.path  # The path of the uploaded file
            try:
                # Replace <receiver_ip_address> with the actual IP address of the receiver.
                receiver_ip = '<receiver_ip_address>'
                subprocess.run(['python', 'fileTransfer\\file_receiver.py', file_path, receiver_ip], check=True)
            except subprocess.CalledProcessError as e:
                # Handle any errors that occur when running the file_sender.py script
                print(f"Error in file sending: {e}")

            # Redirect to shared files or show success message
            return redirect('shared_files')
    else:
        form = FileUploadForm()
    return render(request, 'users/upload_file.html', {'form': form})

@login_required
def shared_files(request):
    files = File.objects.all()  # List all shared files
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
            file_request.requester_ip = ip_address  # Assuming you have a 'requester_ip' field in your FileRequest model
            
            file_request.save()
            return redirect('view_requests')  # Redirect to the page showing all requests
    else:
        form = FileRequestForm()
    return render(request, 'users/request_file.html', {'form': form})

@login_required
def view_requests(request):
    file_requests = FileRequest.objects.all().order_by('-requested_at')  # Get all file requests
    return render(request, 'users/view_requests.html', {'file_requests': file_requests})
