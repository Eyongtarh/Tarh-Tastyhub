from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    pickup_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone_number',
            'street_address1', 'street_address2',
            'town_or_city', 'county', 'postcode', 'local',
            'delivery_type', 'pickup_time'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control mb-2'})
            field.label = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('delivery_type') == 'pickup' and not cleaned.get('pickup_time'):
            self.add_error('pickup_time', 'Pickup time is required for pickup orders.')
        return cleaned
