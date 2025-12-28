from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    '''
    Form for updating user profile information.
    '''
    class Meta:
        model = UserProfile
        fields = (
            'default_phone_number',
            'default_local',
            'default_postcode',
            'default_town_or_city',
            'default_street_address1',
            'default_street_address2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_local': 'Locality',
            'default_postcode': 'Postal Code',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
        }
        for name, field in self.fields.items():
            placeholder = placeholders.get(name, '')
            if field.required:
                placeholder += ' *'
            field.widget.attrs.update({
                'placeholder': placeholder,
                'class': 'form-control mb-2',
            })
            field.label = ''

    def clean_default_phone_number(self):
        phone = self.cleaned_data.get('default_phone_number')
        if phone:
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) < 10:
                raise forms.ValidationError(
                    'Enter a valid phone number with at least 10 digits.'
                )
            return phone.strip()
        return phone

    def clean_default_postcode(self):
        postcode = self.cleaned_data.get('default_postcode')
        if postcode and len(postcode.strip()) < 4:
            raise forms.ValidationError('Postcode is too short.')
        return postcode.strip() if postcode else postcode

    def clean_default_town_or_city(self):
        town = self.cleaned_data.get('default_town_or_city')
        if town and len(town.strip()) < 2:
            raise forms.ValidationError(
                'Town or city name must be at least 2 characters.'
            )
        return town.strip() if town else town

    def clean_default_street_address1(self):
        address = self.cleaned_data.get('default_street_address1')
        if address and len(address.strip()) < 5:
            raise forms.ValidationError(
                'Street address must be at least 5 characters.'
            )
        return address.strip() if address else address

    def clean_default_street_address2(self):
        address = self.cleaned_data.get('default_street_address2')
        return address.strip() if address else address

    def clean_default_local(self):
        local = self.cleaned_data.get('default_local')
        if local and len(local.strip()) < 2:
            raise forms.ValidationError(
                'Locality must be at least 2 characters.'
            )
        return local.strip() if local else local


class UserRegisterForm(UserCreationForm):
    '''
    Form for registering a new user with email validation.
    '''
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and len(username.strip()) < 3:
            raise forms.ValidationError(
                'Username must be at least 3 characters long.'
            )
        return username.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already in use.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password and len(password) < 8:
            raise forms.ValidationError(
                'Password must be at least 8 characters long.'
            )
        return password
