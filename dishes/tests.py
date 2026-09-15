"""
Tests for dishes: the staff-only image upload size validation added to
DishForm/DishImageForm/CategoryForm, and basic view access control.
"""
from decimal import Decimal
from io import BytesIO
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from .forms import CategoryForm, DishForm, DishImageForm
from .models import Category, Dish, DishPortion


def make_small_image_file(name="small.png"):
    """A tiny, real PNG - well under the 5MB limit."""
    buffer = BytesIO()
    Image.new("RGB", (20, 20), color="red").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


def make_oversized_image_file(name="big.bmp"):
    """A real, PIL-openable image whose file size is guaranteed to exceed
    5MB. BMP is used (not PNG/JPEG) because it is uncompressed, so a large
    solid-colour square can't shrink away to a few KB like it would with a
    compressed format."""
    buffer = BytesIO()
    Image.new("RGB", (1600, 1600), color="red").save(buffer, format="BMP")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/bmp")


class ImageUploadSizeValidationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Drinks", slug="drinks")

    def test_dish_form_rejects_image_over_5mb(self):
        large_image = make_oversized_image_file()
        self.assertGreater(large_image.size, 5 * 1024 * 1024)
        form = DishForm(
            data={
                "category": self.category.id,
                "name": "Big Image Dish",
                "slug": "big-image-dish",
                "description": "desc",
                "price": "5.00",
                "available": True,
            },
            files={"image": large_image},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_dish_form_accepts_small_image(self):
        small_image = make_small_image_file()
        form = DishForm(
            data={
                "category": self.category.id,
                "name": "Small Image Dish",
                "slug": "small-image-dish",
                "description": "desc",
                "price": "5.00",
                "available": True,
            },
            files={"image": small_image},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_dish_image_form_rejects_oversized_image(self):
        large_image = make_oversized_image_file("big2.bmp")
        form = DishImageForm(
            data={"alt_text": "big"}, files={"image": large_image}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_category_form_rejects_oversized_icon(self):
        large_image = make_oversized_image_file("icon.bmp")
        form = CategoryForm(
            data={
                "name": "New Category",
                "slug": "new-category",
                "menu_type": "Breakfast",
            },
            files={"icon": large_image},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("icon", form.errors)


class DishViewAccessTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Lunch", slug="lunch")
        self.dish = Dish.objects.create(
            category=self.category,
            name="Test Dish",
            slug="test-dish",
            description="desc",
            price=Decimal("9.99"),
        )
        DishPortion.objects.create(
            dish=self.dish, size="Regular", price=Decimal("9.99")
        )

    def test_dish_list_is_public(self):
        response = self.client.get(reverse("dish_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Dish")

    def test_dish_detail_is_public(self):
        response = self.client.get(reverse("dish_detail", args=["test-dish"]))
        self.assertEqual(response.status_code, 200)

    def test_add_dish_requires_staff(self):
        response = self.client.get(reverse("add_dish"))
        self.assertEqual(response.status_code, 302)

        User.objects.create_user(username="regular", password="testpass12345")
        self.client.login(username="regular", password="testpass12345")
        response = self.client.get(reverse("add_dish"))
        self.assertEqual(response.status_code, 302)

    def test_add_dish_allows_staff(self):
        User.objects.create_user(
            username="staffer", password="testpass12345", is_staff=True
        )
        self.client.login(username="staffer", password="testpass12345")
        response = self.client.get(reverse("add_dish"))
        self.assertEqual(response.status_code, 200)
