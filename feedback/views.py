from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from .forms import FeedbackForm
import logging


logger = logging.getLogger(__name__)


@ratelimit(key="ip", rate="3/m", block=True)
def feedback_view(request):
    """
    Handle user feedback submission.
    Authenticated users automatically have their name and email attached.
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
                    logger.warning("Anonymous feedback missing name/email.")
                    return render(request, 'feedback/feedback.html', {'form': form})

            try:
                feedback.save()
                messages.success(request, "✅ Thanks for your feedback! We'll respond soon.")
                return redirect('feedback')
            except Exception as e:
                logger.error(f"Error saving feedback: {e}")
                messages.error(request, "An error occurred while saving your feedback. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
            logger.warning(f"Feedback form errors: {form.errors}")
    else:
        form = FeedbackForm(user=request.user)

    return render(request, 'feedback/feedback.html', {'form': form})
