from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from django.contrib.admin.views.decorators import staff_member_required
from .forms import FeedbackForm
from .models import Feedback
import logging

logger = logging.getLogger(__name__)


@ratelimit(key="ip", rate="3/m", block=True)
def feedback_view(request):
    """
    User feedback submission view.
    """
    if request.method == 'POST':
        form = FeedbackForm(request.POST, user=request.user)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
                feedback.name = request.user.get_full_name() or request.user.username
                feedback.email = request.user.email
            else:
                if not feedback.name or not feedback.email:
                    messages.error(request, "Name and email are required for anonymous feedback.")
                    return render(request, 'feedback/feedback.html', {'form': form, 'hidden_fields': ['name', 'email']})

            try:
                feedback.save()
                messages.success(request, "Thanks for your feedback!")
                return redirect('feedback')
            except Exception as e:
                logger.error(f"Error saving feedback: {e}")
                messages.error(request, "An error occurred. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FeedbackForm(user=request.user)

    return render(request, 'feedback/feedback.html', {'form': form, 'hidden_fields': ['name', 'email']})


@staff_member_required
def mark_handled(request, pk):
    fb = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        fb.handled = True
        fb.save()
    return redirect('admin_dashboard')


@staff_member_required
def mark_unhandled(request, pk):
    fb = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        fb.handled = False
        fb.save()
    return redirect('admin_dashboard')
