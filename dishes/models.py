from io import BytesIO
from decimal import Decimal
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image, UnidentifiedImageError


class DishQuerySet(models.QuerySet):
    def available(self):
        """Only dishes marked available."""
        return self.filter(available=True)

    def with_portions(self):
        """Prefetch portions to avoid N+1 when rendering menus."""
        return self.prefetch_related('portions')

    def with_images(self):
        """Prefetch additional images."""
        return self.prefetch_related('images')

    def by_menu_type(self, menu_type):
        """Filter dishes whose category.menu_type matches (case-insensitive)."""
        return self.filter(category__menu_type__iexact=menu_type)


class DishManager(models.Manager):
    def get_queryset(self):
        return DishQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().available()

    def with_portions(self):
        return self.get_queryset().with_portions()

    def with_images(self):
        return self.get_queryset().with_images()

    def by_menu_type(self, menu_type):
        return self.get_queryset().by_menu_type(menu_type)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    menu_type = models.CharField(
        max_length=50,
        choices=(
            ('Breakfast', 'Breakfast'),
            ('Lunch', 'Lunch'),
            ('Dinner', 'Dinner'),
            ('Grill', 'Grill'),
            ('Drinks', 'Drinks'),
        ),
        default='Breakfast'  # <-- added default to fix migration
    )
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dish_list_by_category', args=[self.slug])


class Dish(models.Model):
    DIETARY_CHOICES = (
        ('Vegetarian', 'Vegetarian'),
        ('Vegan', 'Vegan'),
        ('Gluten-Free', 'Gluten-Free'),
        ('Spicy', 'Spicy'),
        ('None', 'None'),
    )

    category = models.ForeignKey(Category, related_name='dishes', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True)
    description = models.TextField()
    ingredients = models.TextField(blank=True, null=True)
    dietary_info = models.CharField(max_length=50, choices=DIETARY_CHOICES, blank=True, null=True)
    prep_time = models.PositiveIntegerField(help_text="Preparation time in minutes", blank=True, null=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    calories = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    available = models.BooleanField(default=True)
    is_special = models.BooleanField(default=False)
    available_from = models.TimeField(blank=True, null=True)
    available_until = models.TimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = DishManager()

    class Meta:
        ordering = ('name',)
        constraints = [
            UniqueConstraint(fields=['category', 'slug'], name='unique_category_slug')
        ]
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:180]
            slug = base
            counter = 1
            while Dish.objects.filter(category=self.category, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        if self.available_from and self.available_until:
            if self.available_from > self.available_until:
                raise ValueError("available_from must be before or equal to available_until")

        super().save(*args, **kwargs)
        if self.image:
            try:
                self._compress_image_field('image')
            except Exception:
                pass

    def _compress_image_field(self, field_name, max_size=(1200, 1200), quality=75):
        """
        Compress image stored in ImageField named field_name.
        Overwrites the image file in-place with a compressed JPEG/PNG.
        """
        img_field = getattr(self, field_name)
        if not img_field:
            return

        try:
            img_field.open()
            img = Image.open(img_field)
        except (FileNotFoundError, UnidentifiedImageError, ValueError):
            return

        format = img.format or 'JPEG'
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail(max_size, Image.LANCZOS)

        buffer = BytesIO()
        save_format = 'JPEG'
        img.save(buffer, format=save_format, quality=quality, optimize=True)
        buffer.seek(0)

        filename = img_field.name.rsplit('/', 1)[-1]
        new_name = f"{filename}"
        img_field.save(new_name, ContentFile(buffer.read()), save=False)
        buffer.close()
        super(Dish, self).save(update_fields=[field_name])

    def get_absolute_url(self):
        return reverse('dish_detail', args=[self.slug])

    @property
    def display_price(self):
        return f"{self.price:.2f}"


class DishPortion(models.Model):
    dish = models.ForeignKey(Dish, related_name='portions', on_delete=models.CASCADE)
    size = models.CharField(max_length=50, help_text="Portion size (e.g., Small, Medium, Large)")
    weight = models.PositiveIntegerField(blank=True, null=True, help_text="Weight in grams (optional)")
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        unique_together = ('dish', 'size')
        indexes = [
            models.Index(fields=['dish', 'size']),
        ]

    def __str__(self):
        return f"{self.dish.name} - {self.size}"

    @property
    def unit_price(self):
        return self.price


class DishImage(models.Model):
    dish = models.ForeignKey(Dish, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dish_images/')
    alt_text = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['dish']),
        ]

    def __str__(self):
        return f"Image for {self.dish.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            self._compress_image(max_size=(1600, 1600), quality=75)
        except Exception:
            pass

    def _compress_image(self, max_size=(1600, 1600), quality=75):
        try:
            self.image.open()
            img = Image.open(self.image)
        except (FileNotFoundError, UnidentifiedImageError, ValueError):
            return

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail(max_size, Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)

        filename = self.image.name.rsplit('/', 1)[-1]
        self.image.save(filename, ContentFile(buffer.read()), save=False)
        buffer.close()
        super(DishImage, self).save(update_fields=['image'])
