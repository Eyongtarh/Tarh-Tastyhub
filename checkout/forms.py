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
        label='',
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
            'local',
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

        # Apply global styling to all fields
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = (
                    css + ' form-control mb-2 stripe-style-input'
                ).strip()
            # Placeholder for text inputs
            if not isinstance(field.widget, forms.Select) and not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.setdefault(
                    'placeholder',
                    name.replace('_', ' ').title()
                )
            field.label = ''

    def clean(self):
        cleaned = super().clean()

        # Require pickup_time if delivery_type is pickup
        if cleaned.get('delivery_type') == 'pickup' and not cleaned.get('pickup_time'):
            self.add_error(
                'pickup_time',
                'Pickup time is required for pickup orders.'
            )

        return cleaned
