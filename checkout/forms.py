from django import forms
from django.utils import timezone
from .models import Order
from datetime import timedelta


class OrderForm(forms.ModelForm):
    """
    Form for creating or updating an Order,
    including delivery/pickup logic.
    """
    pickup_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control mb-2 stripe-style-input',
                'placeholder': 'Select pickup time',
            }
        )
    )

    DELIVERY_CHOICES = [
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
    ]

    delivery_type = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Delivery Method',
    )

    card_helper = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(
            attrs={
                'readonly': True,
                'class': 'form-control-plaintext text-muted small mb-2',
                'value': (
                    'Your card details are securely processed by Stripe '
                    'and never stored on our servers.'
                ),
                'tabindex': '-1',
            }
        )
    )

    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone_number', 'street_address1',
            'street_address2', 'town_or_city', 'county', 'postcode',
            'delivery_type', 'pickup_time',
        ]
        widgets = {
            'local': forms.Select(
                attrs={'class': 'form-control mb-2 stripe-style-input'}
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize form with default CSS classes and placeholders.
        """
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_classes = field.widget.attrs.get('class', '')
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = (
                    f'{css_classes} form-control mb-2 stripe-style-input'
                ).strip()
            if not isinstance(field.widget, (forms.Select, forms.RadioSelect)):
                field.widget.attrs.setdefault(
                    'placeholder', name.replace('_', ' ').title()
                )
        for field in self.fields.values():
            field.label = ''

    def clean(self):
        """
        Validate pickup time according to
        delivery type and opening hours.
        """
        cleaned = super().clean()
        delivery_type = cleaned.get('delivery_type')
        pickup_time = cleaned.get('pickup_time')

        if delivery_type == 'pickup':
            if not pickup_time:
                self.add_error(
                    'pickup_time',
                    'Pickup time is required for pickup orders.'
                )
            else:
                now = timezone.now()
                min_time = now + timedelta(minutes=15)
                if pickup_time < min_time:
                    self.add_error(
                        'pickup_time',
                        'Pickup time must be at least 15 minutes from now.'
                    )
                day = pickup_time.weekday()
                hour_decimal = pickup_time.hour + pickup_time.minute / 60
                if 0 <= day <= 4:  # Weekdays
                    if not (7 <= hour_decimal <= 22):
                        self.add_error(
                            'pickup_time',
                            'Pickup time must be between '
                            '07:00 and 22:00 on weekdays.'
                        )
                else:  # Weekends
                    if not (7 <= hour_decimal <= 21):
                        self.add_error(
                            'pickup_time',
                            'Pickup time must be between '
                            '07:00 and 21:00 on weekends.'
                        )

        return cleaned
