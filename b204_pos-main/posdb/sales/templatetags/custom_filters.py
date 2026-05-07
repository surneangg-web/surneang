# sales/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def sum_field(queryset, field_name):
    """Sum a specific field from a queryset of objects"""
    try:
        return sum(float(getattr(obj, field_name)) for obj in queryset)
    except (AttributeError, ValueError, TypeError):
        return 0

@register.filter
def count_with_discount(queryset):
    """Count orders that have a discount applied"""
    count = 0
    for order in queryset:
        try:
            if order.discount:
                count += 1
        except:
            pass
    return count

