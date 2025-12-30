"""
Views for user registration, login, profile management,
email verification, and account actions such as deletion
and order history.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
import logging
from django.contrib.auth.models import User
from checkout.models import Order
from .models import UserProfile
from .forms import UserProfileForm, UserRegisterForm
from .utils import send_verification_email, email_verification_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


def register(request):
    """Register a new user with email verification."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_verification_email(request, user)
            messages.success(
                request,
                "Account created! Please verify your email before logging in."
            )
            return redirect('login')
        else:
            messages.error(
                request,
                "There were errors in your form. Please fix them."
            )
    else:
        form = UserRegisterForm()
    return render(request, 'profiles/register.html', {'form': form})


def login_view(request):
    """Login view with email activation check."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.warning(
                    request,
                    "Your email is not verified. Please check your inbox."
                )
                return redirect('resend_verification')
            login(request, user)
            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )
            return redirect('profile')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'profiles/login.html', {'form': form})


def activate_account(request, uidb64, token):
    """Verify email and activate account."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        logger.warning(f"Activation failed: {e}")
        messages.error(request, "Invalid activation link.")
        return redirect('login')
    if user.is_active:
        messages.info(request, "Your email is already verified.")
        login(request, user)
        return redirect('profile')
    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(
            request,
            "Your email has been verified. Welcome!"
        )
        return redirect('profile')
    messages.error(request, "Activation link expired or invalid.")
    return redirect('login')


def resend_verification(request):
    """
    Resend verification email to user if account is inactive.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                send_verification_email(request, user)
        except User.DoesNotExist:
            pass
        messages.success(
            request,
            "If an account exists for that email, "
            "a verification message has been sent."
        )
        return redirect('login')
    return render(request, 'profiles/resend_verification.html')


@login_required
def profile(request):
    """
    Display and update user profile.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profile updated successfully"
            )
        else:
            messages.error(
                request,
                "Update failed. Please ensure the form is valid."
            )
    else:
        form = UserProfileForm(instance=profile)
    orders = profile.orders.all() if hasattr(profile, 'orders') else []
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def order_history(request, order_number):
    """
    Display a specific order for the logged-in user.
    """
    order = get_object_or_404(Order, order_number=order_number)
    messages.info(
        request,
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    )
    context = {
        'order': order,
        'from_profile': True
    }
    return render(request, 'checkout/checkout_success.html', context)


@login_required
def delete_account(request):
    """
    Delete user account permanently.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(
            request,
            "Your account has been deleted."
        )
        return redirect('home')
    return render(request, 'profiles/delete_account.html')


@login_required
def password_change(request):
    """
    Redirect to Django Allauth password change page.
    """
    return redirect('/accounts/password/change/')
