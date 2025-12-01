from django import forms
from django.core.exceptions import ValidationError
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    # Honeypot field for spam bots
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Pre-fill fields for authenticated users
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email

    def clean_honeypot(self):
        """
        Fail if honeypot is filled (spam bot likely)
        """
        data = self.cleaned_data.get('honeypot')
        if data:
            raise ValidationError("Spam detected.")
        return data

    def clean_email(self):
        """
        Optional: validate email domain, or ensure lowercase
        """
        email = self.cleaned_data.get('email')
        if email:
            return email.lower().strip()
        return email

    def clean_message(self):
        """
        Optional: prevent extremely short or repetitive messages
        """
        message = self.cleaned_data.get('message')
        if message and len(message.strip()) < 10:
            raise ValidationError("Message is too short. Please provide more details.")
        return message
