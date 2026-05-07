# sales/admin.py

from django.contrib import admin
from .models import Discount, Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'price', 'stock', 'is_active', 'has_image']
    list_filter   = ['category', 'is_active']
    search_fields = ['name', 'barcode']
    ordering      = ['name']
    fieldsets     = (
        ('មូលដ្ឋាន', {
            'fields': ('name', 'category', 'barcode', 'is_active'),
        }),
        ('តម្លៃ និងស្តុក', {
            'fields': ('price', 'stock'),
        }),
        ('រូបភាព', {
            'fields': ('image',),
        }),
    )
    
    def has_image(self, obj):
        """Display whether a product has an image"""
        return '✓' if obj.image else '✗'
    has_image.short_description = 'Image'


class OrderItemInline(admin.TabularInline):
    """បង្ហាញ order items ផ្ទាល់នៅក្នុងទំព័រកែ Order"""
    model  = OrderItem
    extra  = 1    # ចំនួនជួរទទេដែលបង្ហាញសម្រាប់បន្ថែម items ថ្មី
    fields = ['product', 'quantity', 'unit_price']


class DiscountInline(admin.StackedInline):
    """បង្ហាញ discount ផ្ទាល់នៅក្នុងទំព័រកែ Order"""
    model  = Discount
    extra  = 0    # មិនបង្ហាញជួរទទេដែលលាប់លាក់ (OneToOne ទេ ForeignKey)
    fields = ['description', 'amount']

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display  = ['order_number', 'description', 'discount_amount', 'order_status']
    search_fields = ['description', 'order__pk']
    ordering      = ['-order__created_at']
    readonly_fields = ['order', 'created_at_display']
    fields = ['order', 'description', 'amount']

    def order_number(self, obj):
        return f"Order #{obj.order.pk}"
    order_number.short_description = "Order"

    def discount_amount(self, obj):
        return f"-${obj.amount}"
    discount_amount.short_description = "Discount"

    def order_status(self, obj):
        status_colors = {
            'open': '⏳ Open',
            'paid': '✓ Paid',
            'refunded': '↩️ Refunded',
            'cancelled': '✕ Cancelled',
        }
        return status_colors.get(obj.order.status, obj.order.status)
    order_status.short_description = "Status"

    def created_at_display(self, obj):
        return obj.order.created_at
    created_at_display.short_description = "Created"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'cashier', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['cashier', 'notes']
    ordering      = ['-created_at']
    inlines       = [OrderItemInline, DiscountInline]    # បង្ហាញ items និង discount នៅក្នុងទម្រង់ order

