from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
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
                'value': 'Your card details are securely processed by Stripe and never stored on our servers.',
                'tabindex': '-1',
            }
        )
    )

    class Meta:
        model = Order
        fields = [
            'full_name',
            'email',
            'phone_number',
            'street_address1',
            'street_address2',
            'town_or_city',
            'county',
            'postcode',
            'delivery_type',
            'pickup_time',
        ]
        widgets = {
            'local': forms.Select(attrs={
                'class': 'form-control mb-2 stripe-style-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')

            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = (
                    css + ' form-control mb-2 stripe-style-input'
                ).strip()

            if not isinstance(field.widget, (forms.Select, forms.RadioSelect)):
                field.widget.attrs.setdefault(
                    'placeholder',
                    name.replace('_', ' ').title()
                )

        for field in self.fields.values():
            field.label = ''

    def clean(self):
        cleaned = super().clean()

        if cleaned.get('delivery_type') == 'pickup' and not cleaned.get('pickup_time'):
            self.add_error(
                'pickup_time',
                'Pickup time is required for pickup orders.'
            )

        return cleaned
