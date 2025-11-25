from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Dish, DishImage, DishPortion


class DishImageInline(admin.TabularInline):
    model = DishImage
    extra = 1
    fields = ('image', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)
    classes = ('collapse',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'


class DishPortionInline(admin.TabularInline):
    model = DishPortion
    extra = 1
    fields = ('size', 'weight', 'price')
    classes = ('collapse',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_type', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'available', 'is_special', 'prep_time', 'calories', 'created', 'updated')
    list_filter = ('available', 'created', 'updated', 'category', 'dietary_info', 'is_special')
    list_editable = ('available', 'is_special')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description', 'ingredients')
    inlines = [DishImageInline, DishPortionInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'
