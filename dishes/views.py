from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.db.models import Q

from .models import Category, Dish
from .forms import DishForm, DishPortionFormSet, DishImageFormSet, CategoryForm


def admin_required(user):
    """Return True if user is staff/admin."""
    return user.is_staff


def get_cached_categories():
    """Return all categories cached for 1 hour."""
    key = "cached_category_menu"
    categories = cache.get(key)
    if not categories:
        categories = Category.objects.all().order_by("name")
        cache.set(key, categories, 3600)
    return categories


def all_dishes(request):
    """Show all dishes with optional search, category filter, and pagination."""
    search_term = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    page = request.GET.get("page", 1)

    categories = get_cached_categories()
    dishes = Dish.objects.available().with_portions().with_images().select_related("category")
    current_category = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        dishes = dishes.filter(category=current_category)

    if search_term:
        dishes = dishes.filter(
            Q(name__icontains=search_term) |
            Q(ingredients__icontains=search_term) |
            Q(dietary_info__icontains=search_term)
        )

    paginator = Paginator(dishes, 8)
    try:
        dishes_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        dishes_page = paginator.page(1)

    return render(
        request,
        "dishes/dishes.html",
        {
            "dishes": dishes_page,
            "categories": categories,
            "current_category": current_category,
            "search_term": search_term,
        }
    )


def dish_list_by_category(request, category_slug):
    """Show all dishes in a category."""
    category = get_object_or_404(Category, slug=category_slug)
    page = request.GET.get("page", 1)
    categories = get_cached_categories()

    cache_key = f"category_dishes_{category_slug}"
    dishes = cache.get(cache_key)

    if not dishes:
        dishes = (
            Dish.objects.available()
            .filter(category=category)
            .with_portions()
            .with_images()
            .select_related("category")
        )
        cache.set(cache_key, dishes, 3600)

    paginator = Paginator(dishes, 12)
    try:
        dishes_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        dishes_page = paginator.page(1)

    return render(
        request,
        "dishes/dishes.html",
        {
            "dishes": dishes_page,
            "categories": categories,
            "current_category": category,
            "search_term": "",
        }
    )


def dish_detail(request, slug):
    """Show details of a dish."""
    cache_key = f"dish_detail_{slug}"
    dish = cache.get(cache_key)

    if not dish:
        dish = get_object_or_404(
            Dish.objects.available()
            .with_portions()
            .with_images()
            .select_related("category"),
            slug=slug
        )
        cache.set(cache_key, dish, 3600)

    return render(request, "dishes/dish_detail.html", {"dish": dish})


@login_required
@user_passes_test(admin_required)
def add_dish(request):
    """Add a new dish (admin only)."""
    form = DishForm(request.POST or None, request.FILES or None)
    portion_formset = DishPortionFormSet(request.POST or None, instance=form.instance)
    image_formset = DishImageFormSet(request.POST or None, request.FILES or None, instance=form.instance)

    if request.method == "POST":
        if form.is_valid() and portion_formset.is_valid() and image_formset.is_valid():
            dish = form.save()
            portion_formset.instance = dish
            portion_formset.save()
            image_formset.instance = dish
            image_formset.save()
            return redirect("dish_list")

    return render(
        request,
        "dishes/add_edit_dish.html",
        {
            "form": form,
            "portion_formset": portion_formset,
            "image_formset": image_formset,
            "action": "Add",
        }
    )


@login_required
@user_passes_test(admin_required)
def edit_dish(request, slug):
    """Edit a dish (admin only)."""
    dish = get_object_or_404(Dish, slug=slug)
    form = DishForm(request.POST or None, request.FILES or None, instance=dish)
    portion_formset = DishPortionFormSet(request.POST or None, instance=dish)
    image_formset = DishImageFormSet(request.POST or None, request.FILES or None, instance=dish)

    if request.method == "POST":
        if form.is_valid() and portion_formset.is_valid() and image_formset.is_valid():
            form.save()
            portion_formset.save()
            image_formset.save()
            cache.delete(f"dish_detail_{slug}")
            return redirect("dish_detail", slug=dish.slug)

    return render(
        request,
        "dishes/add_edit_dish.html",
        {
            "form": form,
            "portion_formset": portion_formset,
            "image_formset": image_formset,
            "action": "Edit",
        }
    )


@login_required
@user_passes_test(admin_required)
def delete_dish(request, slug):
    """Delete a dish (admin only)."""
    dish = get_object_or_404(Dish, slug=slug)
    if request.method == "POST":
        dish.delete()
        cache.delete(f"dish_detail_{slug}")
        return redirect("dish_list")
    return render(request, "dishes/delete_dish.html", {"dish": dish})


@login_required
@user_passes_test(admin_required)
def add_category(request):
    """Add a category (admin only)."""
    form = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        cache.delete("cached_category_menu")
        return redirect("dish_list")
    return render(request, "dishes/add_edit_category.html", {"form": form, "action": "Add"})


@login_required
@user_passes_test(admin_required)
def edit_category(request, slug):
    """Edit a category (admin only)."""
    category = get_object_or_404(Category, slug=slug)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        cache.delete("cached_category_menu")
        cache.delete(f"category_dishes_{slug}")
        return redirect("dish_list_by_category", category_slug=category.slug)
    return render(request, "dishes/add_edit_category.html", {"form": form, "action": "Edit"})


@login_required
@user_passes_test(admin_required)
def delete_category(request, slug):
    """Delete a category (admin only)."""
    category = get_object_or_404(Category, slug=slug)
    if request.method == "POST":
        category.delete()
        cache.delete("cached_category_menu")
        cache.delete(f"category_dishes_{slug}")
        return redirect("dish_list")
    return render(request, "dishes/delete_category.html", {"category": category})
