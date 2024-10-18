from django.contrib import admin
from django.urls import path
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('login/', user_views.login_view, name='login'),
    path('dashboard/', user_views.dashboard, name='dashboard'), 
    path('logout/', user_views.logout_view, name='logout'),
    path('upload/', user_views.upload_file, name='upload_file'),
    path('shared-files/', user_views.shared_files, name='shared_files'),
    path('request-file/', user_views.request_file, name='request_file'),
    path('view-requests/', user_views.view_requests, name='view_requests'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
