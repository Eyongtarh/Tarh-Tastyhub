from django import forms
from .models import Dish, Category


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = (
            'category',
            'name',
            'slug',
            'description',
            'ingredients',
            'dietary_info',
            'prep_time',
            'calories',
            'image',
            'price',
            'available',
            'is_special',
            'available_from',
            'available_until',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mb-2'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug', 'menu_type', 'description', 'icon')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control mb-2'
