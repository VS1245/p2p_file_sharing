from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class File(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)  # File uploaded by a specific user
    file = models.FileField(upload_to='uploads/')  # Path to store uploaded files
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Automatically add the time the file is uploaded

    def __str__(self):
        return f"{self.file.name} uploaded by {self.uploader.username}"


class FileRequest(models.Model):
    file_name = models.CharField(max_length=100)
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Add the ip_address field

    def __str__(self):
        return f"{self.file_name} requested by {self.requester.username}"
