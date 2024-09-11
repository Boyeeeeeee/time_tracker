from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import logout
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from .models import Profile


def register(request):
    if request.method == 'POST':

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

class CustomLogoutView(View):
    def get(self, request):
        # Perform the logout action
        logout(request)
        # Redirect to the login page or render a logout confirmation page
        return render(request, 'users/logout.html')

    def post(self, request):
        # Perform the logout action (redundant but ensures logout on POST as well)
        logout(request)
        return redirect('login')
    



@login_required
def profile(request):
    try:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('profile')
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)
    except ObjectDoesNotExist:
        Profile.objects.create(user=request.user)  # Create profile if it doesn't exist
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)
