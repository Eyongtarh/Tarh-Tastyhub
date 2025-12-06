from django import forms
from django.forms import inlineformset_factory
from .models import Dish, Category, DishImage, DishPortion


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


class DishPortionForm(forms.ModelForm):
    class Meta:
        model = DishPortion
        fields = ('size', 'weight', 'price')


DishPortionFormSet = inlineformset_factory(
    Dish,
    DishPortion,
    form=DishPortionForm,
    extra=1,
    can_delete=True
)


class DishImageForm(forms.ModelForm):
    class Meta:
        model = DishImage
        fields = ('image', 'alt_text')


DishImageFormSet = inlineformset_factory(
    Dish,
    DishImage,
    form=DishImageForm,
    extra=2,
    can_delete=True
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug', 'menu_type', 'description', 'icon')
