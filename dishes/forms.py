"""
Forms for managing Dish, DishPortion, DishImage, and Category models.
(ModelForms and inline formsets for portions and images)
"""
from django import forms
from django.forms import inlineformset_factory
from .models import Dish, Category, DishImage, DishPortion

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def validate_image_size(image):
    """Reject uploads above MAX_IMAGE_SIZE_BYTES."""
    if image and image.size > MAX_IMAGE_SIZE_BYTES:
        raise forms.ValidationError(
            "Image file too large (maximum size is 5 MB)."
        )


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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_image_size(image)
        return image


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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_image_size(image)
        return image


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

    def clean_icon(self):
        icon = self.cleaned_data.get('icon')
        validate_image_size(icon)
        return icon
