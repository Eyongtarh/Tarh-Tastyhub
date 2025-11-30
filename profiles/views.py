from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from datetime import timedelta
import logging

from .models import UserProfile
from .forms import UserProfileForm, UserRegisterForm
from .utils import email_verification_token, send_verification_email
from checkout.models import Order
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


@ratelimit(key="ip", rate="5/m", block=True)
def register(request):
    """User registration view with email verification"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Disable login until email verified
            user.save()

            # DO NOT manually create profile here; signals will create UserProfile on user creation.
            # Ensure email_verified flag is False by default in the model (it is).

            # Send verification email
            send_verification_email(request, user)
            messages.success(request, "✅ Account created! Please verify your email to log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration error. Please correct the fields below.")
    else:
        form = UserRegisterForm()
    return render(request, 'profiles/register.html', {'form': form})


@ratelimit(key="ip", rate="5/m", block=True)
def login_view(request):
    """Custom login handling for unverified emails"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.userprofile.email_verified:
                messages.warning(request, "Email not verified. Check your inbox or resend verification.")
                return redirect('resend_verification_email')
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'profiles/login.html', {'form': form})


@login_required
def resend_verification_email(request):
    """Resend email verification with cooldown"""
    profile = getattr(request.user, 'userprofile', None)
    if not profile:
        messages.error(request, "Profile not found for your account.")
        return redirect('profile')

    now = timezone.now()

    if profile.email_verified:
        messages.info(request, "Your email is already verified.")
        return redirect('profile')

    if profile.last_verification_sent and (now - profile.last_verification_sent) < timedelta(minutes=5):
        messages.warning(request, "Too soon to resend verification email. Please wait a few minutes.")
        return redirect('profile')

    success = send_verification_email(request, request.user)
    if success:
        messages.success(request, "Verification email sent again. Check your inbox.")
    else:
        messages.error(request, "Failed to send verification email. Try again later.")
    return redirect('profile')


def activate_account(request, uidb64, token):
    """Activate account via verification email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError) as e:
        logger.warning(f"Activation error: {e}")
        messages.error(request, "Invalid verification link.")
        return redirect('login')

    profile = getattr(user, 'userprofile', None)
    if not profile:
        messages.error(request, "Profile not found.")
        return redirect('login')

    if profile.email_verified:
        messages.info(request, "Account already verified. You can login.")
        login(request, user)
        return redirect('profile')

    if email_verification_token.check_token(user, token):
        profile.email_verified = True
        profile.save(update_fields=['email_verified'])
        user.is_active = True
        user.save(update_fields=['is_active'])
        login(request, user)
        messages.success(request, "Email verified! You are now logged in.")
        return redirect('profile')
    else:
        messages.error(request, "Verification link is invalid or expired.")
        return redirect('login')


@login_required
def profile(request):
    """View and update user profile, show order history"""
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
        else:
            messages.error(request, "Error updating your profile. Check the form fields.")
    else:
        form = UserProfileForm(instance=profile)

    orders = profile.orders.all()

    return render(request, 'profiles/profile.html', {
        'form': form,
        'orders': orders,
    })


@login_required
def order_history(request, order_number):
    """View a specific order from profile"""
    order = get_object_or_404(Order, order_number=order_number, user_profile=request.user.userprofile)
    messages.info(request, f"Order details for {order_number}")
    return render(request, 'checkout/checkout_success.html', {
        'order': order,
        'from_profile': True
    })


@login_required
def delete_account(request):
    """Delete the logged-in user's account"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    return render(request, 'profiles/delete_account.html')
