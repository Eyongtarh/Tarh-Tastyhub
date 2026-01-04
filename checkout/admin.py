from django.contrib import admin
from .models import Order, OrderLineItem
from django.utils.html import format_html


class OrderLineItemInline(admin.TabularInline):
    """
    Allows editing OrderLineItem objects
    inline within the Order admin page.
    """
    model = OrderLineItem
    fields = ('portion', 'quantity', 'price', 'lineitem_total')
    readonly_fields = ('lineitem_total',)
    extra = 0

    def lineitem_total(self, obj):
        """
        Display the total price for this line item
        formatted to 2 decimal places.
        """
        return f"{obj.lineitem_total:.2f}"
    lineitem_total.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for Order model.
    """
    list_display = (
        'order_number', 'full_name', 'local', 'delivery_type',
        'pickup_time', 'status', 'grand_total', 'date',
    )
    list_filter = ('delivery_type', 'status', 'date')
    search_fields = (
        'order_number', 'full_name', 'email',
        'phone_number', 'local',
    )
    ordering = ('-date',)
    inlines = [OrderLineItemInline]

    def get_queryset(self, request):
        """
        Customize the queryset to prefetch related objects for efficiency.
        Prefetch lineitems -> portion -> dish to reduce database queries.
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            'lineitems__portion__dish'
        )
