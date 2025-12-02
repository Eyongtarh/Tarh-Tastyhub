from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from datetime import timedelta
import logging

from django.contrib.auth.models import User
from checkout.models import Order
from .models import UserProfile
from .forms import UserProfileForm, UserRegisterForm
from .utils import email_verification_token, send_verification_email

logger = logging.getLogger(__name__)


@ratelimit(key="ip", rate="5/m", block=True)
def register(request):
    """
    Register a new user (email verification required).
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email verification before login
            user.save()  # Signal creates UserProfile

            send_verification_email(request, user)

            messages.success(
                request,
                "Account created! Please verify your email before logging in."
            )
            return redirect('login')
        else:
            messages.error(request, "There were errors in your form. Please fix them.")
    else:
        form = UserRegisterForm()

    return render(request, 'profiles/register.html', {'form': form})



@ratelimit(key="ip", rate="5/m", block=True)
def login_view(request):
    """
    Users cannot log in unless their email is verified.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if not user.userprofile.email_verified:
                messages.warning(
                    request,
                    "Your email is not verified. Please check your email or resend verification."
                )
                return redirect('resend_verification')

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('profile')

        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'profiles/login.html', {'form': form})


@login_required
def resend_verification_email(request):
    """
    Allow user to resend verification email with 5-minute cooldown.
    """
    profile = request.user.userprofile
    now = timezone.now()

    if profile.email_verified:
        messages.info(request, "Your email is already verified.")
        return redirect('profile')

    if profile.last_verification_sent and (now - profile.last_verification_sent) < timedelta(minutes=5):
        messages.warning(request, "Please wait a few minutes before resending verification.")
        return redirect('profile')

    send_verification_email(request, request.user)
    messages.success(request, "A new verification email has been sent.")
    return redirect('profile')


def activate_account(request, uidb64, token):
    """
    Verify the email link, activate account, and log the user in.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except Exception as e:
        logger.warning(f"Activation failed: {e}")
        messages.error(request, "Invalid activation link.")
        return redirect('login')

    profile = user.userprofile

    if profile.email_verified:
        messages.info(request, "Your email is already verified.")
        login(request, user)
        return redirect('profile')

    if email_verification_token.check_token(user, token):
        profile.email_verified = True
        profile.save()

        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, "Your email has been verified. Welcome!")
        return redirect('profile')

    messages.error(request, "Activation link expired or invalid.")
    return redirect('login')


@login_required
def profile(request):
    """
    Show and update user profile. Always ensures profile exists (fixes 404).
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = UserProfileForm(instance=profile)

    orders = Order.objects.filter(user_profile=profile)

    return render(request, 'profiles/profile.html', {
        'form': form,
        'orders': orders,
    })


@login_required
def order_history(request, order_number):
    """
    Display a specific order from the user's profile.
    """
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user_profile=request.user.userprofile
    )

    messages.info(request, f"Viewing order #{order_number}")

    return render(request, 'checkout/checkout_success.html', {
        'order': order,
        'from_profile': True
    })


@login_required
def delete_account(request):
    """
    Permanently delete the user's account.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()

        messages.success(request, "Your account has been deleted.")
        return redirect('home')

    return render(request, 'profiles/delete_account.html')


@login_required
def password_change(request):
    """
    Redirect to Django Allauth password change URL.
    """
    return redirect('/accounts/password/change/')
