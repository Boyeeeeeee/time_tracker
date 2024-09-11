"""
URL configuration for time_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from core import views
from users.views import CustomLogoutView
from core.views import home,update_goal, delete_goal, update_wish, delete_wish
from users import views as user_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', login_required(views.dashboard), name='dashboard'),
    path('admin/', admin.site.urls),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('add_goal/', login_required(views.add_goal), name='add_goal'),
    path('add_wish/', login_required(views.add_wish), name='add_wish'),
    path('goal/<int:pk>/update/', login_required(views.update_goal), name='update_goal'),
    path('goal/<int:pk>/delete/', login_required(views.delete_goal), name='delete_goal'),
    path('wish/<int:pk>/update/', login_required(views.update_wish), name='update_wish'),
    path('wish/<int:pk>/delete/', login_required(views.delete_wish), name='delete_wish'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', login_required(user_views.profile), name='profile'),  # Profile page URL
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    
    path('allocate/<int:goal_id>/', login_required(views.allocate_time), name='allocate_time'),
    path('allocated-times/', login_required(views.allocated_times), name='allocated_times'),
    path('delete_allocation/<int:allocation_id>/', login_required(views.delete_allocation), name='delete_allocation'),
    path('sync-calendar/', views.sync_with_google_calendar, name='sync_with_google_calendar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)