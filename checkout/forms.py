from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    pickup_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control mb-2'
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
            'local',
            'delivery_type',
            'pickup_time',
        ]
        widgets = {
            'delivery_type': forms.Select(attrs={'class': 'form-control mb-2'}),
            'local': forms.Select(attrs={'class': 'form-control mb-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply bootstrap formatting and hide labels
        for name, field in self.fields.items():
            # Add class if widget does not have one
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing_classes + ' form-control mb-2').strip()

            # Hide labels (correct way)
            field.label = ''

            # Add placeholder text
            field.widget.attrs.setdefault('placeholder', name.replace('_', ' ').title())

    def clean(self):
        cleaned = super().clean()

        # Require pickup_time if delivery_type == "pickup"
        if cleaned.get('delivery_type') == 'pickup' and not cleaned.get('pickup_time'):
            self.add_error('pickup_time', 'Pickup time is required for pickup orders.')

        return cleaned
