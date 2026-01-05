from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, RegistrationForm, UserProfileForm
from .models import User


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect_user_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # seller checkbox
            if request.POST.get('is_seller'):
                user.is_staff = True
                messages.success(
                    request,
                    'Seller account created successfully! Please login to continue.'
                )
            else:
                messages.success(
                    request,
                    'Account created successfully! Please login to continue.'
                )
            user.save()
            return redirect('accounts:login')   # ✅ ONLY ONE RESPONSE

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """View and edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


def redirect_user_by_role(user):
    """Redirect user based on their role"""
    if user.is_superuser or user.is_staff:
        return redirect('dashboard:admin_dashboard')
    elif user.is_seller:
        return redirect('dashboard:seller_dashboard')
    else:
        return redirect('home')
