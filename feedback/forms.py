from django import forms
from django.core.exceptions import ValidationError
from .models import Feedback


class FeedbackForm(forms.ModelForm):
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
        if user and user.is_authenticated:
            self.fields['name'].initial = user.get_full_name() or user.username
            self.fields['email'].initial = user.email

    def clean_honeypot(self):
        '''
        Fail if honeypot is filled (spam bot likely)
        '''
        data = self.cleaned_data.get('honeypot')
        if data:
            raise ValidationError('Spam detected.')
        return data

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return name.strip()

    def clean_email(self):
        '''
        Ensure email is lowercase and valid
        '''
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        email = email.lower().strip()
        if '@' not in email:
            raise ValidationError('Enter a valid email address.')
        return email

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject or len(subject.strip()) < 3:
            raise ValidationError('Subject must be at least 3 characters long.')
        return subject.strip()

    def clean_message(self):
        '''
        Prevent extremely short or repetitive messages
        '''
        message = self.cleaned_data.get('message')
        if not message or len(message.strip()) < 10:
            raise ValidationError('Message is too short. Please provide more details.')
        return message.strip()
