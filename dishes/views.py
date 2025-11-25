from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache

from .models import Category, Dish
from .forms import DishForm, CategoryForm


def admin_required(user):
    """Check if user is staff/admin."""
    return user.is_staff


def get_cached_categories():
    """Cache category list for 1 hour."""
    key = "cached_category_menu"
    categories = cache.get(key)
    if not categories:
        categories = Category.objects.all().order_by("name")
        cache.set(key, categories, 3600)  # 1 hour
    return categories


def all_dishes(request):
    """
    Display all dishes with:
    - Pagination
    - Search
    - Category filtering
    - Cached categories
    - Optimized QuerySets
    """
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
        dishes = dishes.filter(name__icontains=search_term)

    paginator = Paginator(dishes, 12)
    try:
        dishes_page = paginator.page(page)
    except PageNotAnInteger:
        dishes_page = paginator.page(1)
    except EmptyPage:
        dishes_page = paginator.page(paginator.num_pages)

    context = {
        "dishes": dishes_page,
        "categories": categories,
        "current_category": current_category,
        "search_term": search_term,
    }
    return render(request, "dishes/dishes.html", context)


def dish_list_by_category(request, category_slug):
    """
    Show dishes under a category.
    Cached results for faster rendering.
    """
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
    except PageNotAnInteger:
        dishes_page = paginator.page(1)
    except EmptyPage:
        dishes_page = paginator.page(paginator.num_pages)

    return render(
        request,
        "dishes/dishes.html",
        {
            "dishes": dishes_page,
            "categories": categories,
            "current_category": category,
            "search_term": "",
        },
    )


def dish_detail(request, slug):
    """
    Show dish details.
    Cached for faster access & optimized QuerySets.
    """
    cache_key = f"dish_detail_{slug}"
    dish = cache.get(cache_key)

    if not dish:
        dish = (
            get_object_or_404(
                Dish.objects.available()
                .with_portions()
                .with_images()
                .select_related("category"),
                slug=slug,
            )
        )
        cache.set(cache_key, dish, 3600)

    return render(request, "dishes/dish_detail.html", {"dish": dish})


def search_dishes(request):
    """AJAX autocomplete search."""
    q = request.GET.get("q", "").strip()

    dishes = (
        Dish.objects.available()
        .filter(name__icontains=q)
        .order_by("name")[:10]
    )

    data = [{"name": d.name, "url": d.get_absolute_url()} for d in dishes]

    return JsonResponse({"dishes": data})


@login_required
@user_passes_test(admin_required)
def add_dish(request):
    if request.method == "POST":
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dish_list")
    else:
        form = DishForm()

    return render(request, "dishes/add_edit_dish.html", {"form": form, "action": "Add"})


@login_required
@user_passes_test(admin_required)
def edit_dish(request, slug):
    dish = get_object_or_404(Dish, slug=slug)

    if request.method == "POST":
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            form.save()
            cache.delete(f"dish_detail_{slug}")  # Invalidate cache
            return redirect("dish_detail", slug=dish.slug)
    else:
        form = DishForm(instance=dish)

    return render(request, "dishes/add_edit_dish.html", {"form": form, "action": "Edit"})


@login_required
@user_passes_test(admin_required)
def delete_dish(request, slug):
    dish = get_object_or_404(Dish, slug=slug)

    if request.method == "POST":
        dish.delete()
        cache.delete(f"dish_detail_{slug}")  # Invalidate cache
        return redirect("dish_list")

    return render(request, "dishes/delete_dish.html", {"dish": dish})


@login_required
@user_passes_test(admin_required)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            cache.delete("cached_category_menu")
            return redirect("dish_list")
    else:
        form = CategoryForm()

    return render(
        request,
        "dishes/add_edit_category.html",
        {"form": form, "action": "Add"},
    )


@login_required
@user_passes_test(admin_required)
def edit_category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            cache.delete("cached_category_menu")
            cache.delete(f"category_dishes_{slug}")
            return redirect("dish_list_by_category", category_slug=category.slug)
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "dishes/add_edit_category.html",
        {"form": form, "action": "Edit"},
    )

@login_required
@user_passes_test(admin_required)
def delete_category(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == "POST":
        category.delete()
        cache.delete("cached_category_menu")
        cache.delete(f"category_dishes_{slug}")
        return redirect("dish_list")

    return render(
        request,
        "dishes/delete_category.html",
        {"category": category},
    )
