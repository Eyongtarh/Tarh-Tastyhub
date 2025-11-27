from django.contrib import admin
from .models import Order, OrderLineItem
from django.utils.html import format_html


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    fields = ('portion', 'quantity', 'price', 'lineitem_total')
    readonly_fields = ('lineitem_total',)
    extra = 0

    def lineitem_total(self, obj):
        return f"{obj.lineitem_total:.2f}"
    lineitem_total.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'full_name', 'local', 'delivery_type',
        'pickup_time', 'status', 'grand_total', 'date'
    )
    list_filter = ('delivery_type', 'status', 'date')
    search_fields = ('order_number', 'full_name', 'email', 'phone_number', 'local')
    ordering = ('-date',)
    inlines = [OrderLineItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('lineitems__portion__dish')
